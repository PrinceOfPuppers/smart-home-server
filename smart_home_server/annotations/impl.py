import types
from typing import (
    Annotated,
    Union,
    TypeVar,
    Type,
    get_origin,
    get_args,
    get_type_hints,
)
from dataclasses import (
    dataclass,
    fields,
    Field,
    is_dataclass,
    MISSING,
    asdict,
)

from functools import cache
from dacite import from_dict
import copy


@dataclass(frozen=True)
class TypeConstraints:
    @property
    def schemaType(self) -> str:
        raise NotImplemented("TypeConstraints missing schema type")

@dataclass(frozen=True)
class IntConstraints(TypeConstraints):
    maximum: int | None = None
    minimum: int | None = None

    @property
    def schemaType(self):
        return "integer"



@dataclass(frozen=True)
class StrConstraints(TypeConstraints):
    maxLength: int | None = None
    minLength: int | None = None
    pattern: str | None = None

    @property
    def schemaType(self):
        return "string"

@dataclass(frozen=True)
class ConstConstraints(TypeConstraints):

    @property
    def schemaType(self):
        return "const"

    @staticmethod
    def create_discriminator(dcls, discriminator_name:str):
        dcls.__dataclass_fields__[discriminator_name] = copy.copy(dcls.__dataclass_fields__[discriminator_name])
        dcls.__dataclass_fields__[discriminator_name].default = dcls.__name__
        setattr(dcls,discriminator_name, dcls.__name__)

@dataclass(frozen=True)
class BoolConstraints(TypeConstraints):

    @property
    def schemaType(self):
        return "boolean"

@dataclass(frozen=True)
class EnumConstraints(TypeConstraints):
    values: set

    @property
    def schemaType(self):
        return "enum"

@dataclass(frozen=True)
class ObjectConstraints(TypeConstraints):
    @property
    def schemaType(self):
        return "object"


@dataclass(frozen=True)
class ArrayConstraints(TypeConstraints):
    minItems: int|None = None
    maxItems: int|None = None
    @property
    def schemaType(self):
        return "array"



@dataclass(frozen=True)
class FormInfo: # must be in all annotations
    label: str | None = None # defaults to the name of the variable
    required: bool = True # overriden by defaults


# =========================
# Helpers
# =========================

def filterNone(l:list):
    return [x for x in l if x is not None]

def unwrap_annotated(annotation):
    """Return (base_type, metadata[])"""
    metadata = []
    while get_origin(annotation) is Annotated:
        annotation, *meta = get_args(annotation)
        metadata.extend(meta)
    return annotation, metadata


def is_union(annotation):
    return get_origin(annotation) in {Union, types.UnionType}


def is_optional(annotation):
    return is_union(annotation) and type(None) in get_args(annotation)


def is_dataclass_type(t):
    return isinstance(t, type) and is_dataclass(t)


def is_polymorphic_base(t):
    return is_dataclass_type(t) and bool(t.__subclasses__())


# =========================
# Primitive / Scalar Schema
# =========================

def get_type_constraints(metadata):
    for meta in metadata:
        if isinstance(meta, TypeConstraints):
            return meta
    return None


def schema_from_primitive(annotation, metadata, default):
    """Generate schema for primitive types with constraints"""
    schema = {}

    type_constraint = get_type_constraints(metadata)
    if type_constraint is None:
        return None
    #assert type_constraint is not None, f"Missing TypeConstraint for {annotation}"

    # Const
    if isinstance(type_constraint, ConstConstraints):
        assert default is not MISSING
        return {"const": default}

    # Enum
    if isinstance(type_constraint, EnumConstraints):
        s = {"enum": list(type_constraint.values)}
        #if default is not MISSING:
        #    s["default"] = default
        return s

    # ObjectConstraint (dataclass)
    if isinstance(type_constraint, ObjectConstraints):
        return schema_for_annotation(annotation)

    # Scalar (int/str/boolean)
    schema["type"] = type_constraint.schemaType
    schema.update({
        k: v for k, v in vars(type_constraint).items()
        if v is not None and k != "schemaType"
    })
    #if default is not MISSING:
    #    schema["default"] = default

    return schema


# =========================
# Recursive Schema Generator
# =========================

def schema_for_annotation(annotation, metadata=None, default=MISSING):
    metadata = metadata or []
    annotation, ann_metadata = unwrap_annotated(annotation)
    metadata = metadata + ann_metadata

    # ---- Union / Optional ----
    if is_union(annotation):
        args = [a for a in get_args(annotation) if a is not type(None)]
        #nullable = type(None) in get_args(annotation)
        if len(args) == 1:
            schema = schema_for_annotation(args[0], metadata, default)
            #if nullable:
            #    schema["nullable"] = True
            return schema
        return {
            "oneOf": filterNone([schema_for_annotation(a, metadata, default) for a in args])
        }

    # ---- Polymorphic base ----
    if is_polymorphic_base(annotation):
        return {"oneOf": filterNone([schema_for_annotation(sub) for sub in annotation.__subclasses__()])}

    # ---- Dataclass ----
    if is_dataclass_type(annotation):
        schema = {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        }
        hints = get_type_hints(annotation, include_extras=True)
        for f in fields(annotation):
            field_annotation = hints[f.name]
            field_default = f.default

            # NOTE: this may break some things
            if field_default is MISSING and f.default_factory is not MISSING:
                field_default = f.default_factory()

            field_schema = schema_for_annotation(field_annotation, None, field_default)
            if field_schema is None:
                continue
            schema["properties"][f.name] = field_schema
            if field_default is MISSING:
                schema["required"].append(f.name)
        if not schema["required"]:
            del schema["required"]
        return schema

    # ---- List / Array ----
    origin = get_origin(annotation)
    if origin is list:
        item_type = get_args(annotation)[0]
        items = schema_for_annotation(item_type)
        type_constraint = get_type_constraints(metadata)
        if items is None or type_constraint is None:
            return None
        #assert type_constraint is not None
        schema = {
            k: v for k, v in vars(type_constraint).items()
            if v is not None and k != "schemaType"
        }
        schema["type"] = type_constraint.schemaType
        schema["items"] = items
        return schema

    # ---- Primitive / scalar ----
    return schema_from_primitive(annotation, metadata, default)

@cache
def json_schema_from_dataclass(cls):
    return schema_for_annotation(cls)


def to_json(x):
    return asdict(x)

T = TypeVar('T')  # Declare a type variable
def from_json(base_class:Type[T], data:dict, discriminator:str|None = None) -> T:
    subclass = base_class
    if discriminator is not None:
        for sc in base_class.__subclasses__():
            if sc.__qualname__ == data[discriminator]:
                subclass = sc
                break
        else:
            raise ValueError("class discriminator not found!")

    return from_dict(subclass, data)
