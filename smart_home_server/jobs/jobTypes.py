from dataclasses import dataclass, field
from typing import Annotated

import smart_home_server.annotations as ann
from functools import cache

# allows properties to be read by asdict
# this determines which properties will be sent to frontend
@dataclass(frozen=True)
class _Job:
    pass

@dataclass(kw_only=True, frozen=True)
class Job(_Job):
    jobType:Annotated[
        str,
        ann.ConstConstraints()
    ] = field(init=False)

    enabled:Annotated[
        bool,
        ann.BoolConstraints()
    ] = True

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        ann.ConstConstraints.create_discriminator(cls, "jobType")

    # override this method to sanitize data or throw exception
    @staticmethod
    def sanitize(data: dict):
        return data

    @staticmethod
    def fromjson(j:dict) -> 'Job':
        return ann.from_json(Job, j, "jobType", lambda dclass, data: dclass.sanitize(data))

    def toJson(self) -> dict:
        return ann.to_json(self)

    @classmethod
    def getSchema(cls):
        return ann.json_schema_from_dataclass(cls)

    # returns dict {datasourceType: schema}
    @classmethod
    @cache
    def getSchemaTypeDict(cls):
        x = cls.getSchema()
        assert x is not None
        jobSchemas = x['oneOf']
        assert isinstance(jobSchemas, list)

        res = {}
        for schema in jobSchemas:
            jType = schema["properties"]["jobType"]["const"]
            res[jType] = schema
        return res


@dataclass(kw_only=True, frozen=True)
class JobPress(Job):
    remoteId:Annotated[
        str,
        ann.StrConstraints()
    ]
    channel:Annotated[
        int,
        ann.IntConstraints()
    ]

@dataclass(kw_only=True, frozen=True)
class JobReboot(Job):
    pass

@dataclass(kw_only=True, frozen=True)
class JobUpdate(Job):
    pass

@dataclass(kw_only=True, frozen=True)
class JobLCD(Job):
    lcdNum:Annotated[
        int,
        ann.IntConstraints()
    ]

    backlight:Annotated[
        str,
        ann.EnumConstraints(values = {"toggle", "on", "off", "same"})
    ] = "same"

@dataclass(kw_only=True, frozen=True)
class JobDelay(Job):
    seconds:Annotated[
        int,
        ann.IntConstraints()
    ] = 0
    minutes:Annotated[
        int,
        ann.IntConstraints()
    ] = 0
    hours:Annotated[
        int,
        ann.IntConstraints()
    ] = 0

@dataclass(kw_only=True, frozen=True)
class JobMacro(Job):
    macroId:Annotated[
        str,
        ann.StrConstraints()
    ]

