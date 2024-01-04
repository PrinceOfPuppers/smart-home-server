import smart_home_server.constants as const

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

patchLcdSchema = \
{
    "type": "object",
    "properties": {
        "num": { "type": "integer", "minimum": 0 },
        "name": nameSchema, # defaults to no change
        "fmt": {"type": "string", "minLength": 0, "maxLength": 200}, # defaults to no change
        "backlight": {"enum": ["toggle", "on", "off"]}, #defaults to no change
    },
    "required": ["num"],
    'additionalProperties': False,
}


rebootSchema = \
{
    "type": "object",
    "properties": {},
    "required": [],
    'additionalProperties': False,
}
updateSchema = \
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
    ('lcd',   patchLcdSchema),
    ('reboot', rebootSchema),
    ('update', updateSchema),
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

