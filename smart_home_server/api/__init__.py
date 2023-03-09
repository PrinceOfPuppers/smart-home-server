
nameSchema = {"type": "string", "minLength": 0, "maxLength": 20, "pattern": "^[^\n\r]*$"}
idSchema   = {"type": "string", "minLength": 0, "maxLength": 50, "pattern": "^[^\n\r]*$"}

postRemoteSchema = \
{
    "type": "object",
    "properties": {
        "id": idSchema,
        "channel": { "type": "integer", "minimum": 0 }, # defaults to 0, validated in function
        "value": { "type": "boolean" } # defaults to True
    },
    "required": ['id'],
    'additionalProperties': False,
}


postLCDSchema = \
{
    "type": "object",
    "properties": {
        "line1":      {"type": "string", "minLength": 0, "maxLength": 70}, # defaults to no change
        "line2":      {"type": "string", "minLength": 0, "maxLength": 70}, # defaults to no change
        "backlight":  {"type": "boolean"}
    },
    "required": [],
    'additionalProperties': False,
}
rebootSchema = \
{
    "type": "object",
    "properties": {},
    "required": [],
    'additionalProperties': False,
}
macroJobSchema = \
{
    "type": "object",
    "properties": {
        "id": idSchema,
    },
    "required": ["id"],
    'additionalProperties': False,
}

_schemas = [
    ('press', postRemoteSchema),
    ('lcd', postLCDSchema),
    ('reboot', rebootSchema),
    ('macro', macroJobSchema),
]

allJobsSchema = [
    {
        "type": "object",
        "properties": {
            "type": {"const": name},
            "data": schema,
        },
        "required": ["type", "data"],
        'additionalProperties': False,
    } for name, schema in _schemas
]

# currently only updates name
patchNameSchema = \
{
    "type": "object",
    "properties":{
        "id":        idSchema,
        "name":      nameSchema,
    },
    "required": ['id', 'name'],
    'additionalProperties': False,
}

