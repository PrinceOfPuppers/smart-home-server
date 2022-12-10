import smart_home_server.constants as const
from smart_home_server.threads.presser import presserAppend
from smart_home_server.threads.lcd import updateLCDFromJobData

postRemoteSchema = \
{
    "type": "object",
    "properties": {
        "channel": { "type": "integer", "minimum": 0, "maximum": len(const.txChannels)-1}, # defaults to 0
        "value": { "type": "boolean" } # defaults to True
    },
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

_schemas = [
    ('press', postRemoteSchema),
    ('lcd', postLCDSchema),
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

def runJob(job:dict):
    # job must contain key 'do'
    if not job['enabled']:
        return

    do = job['do']
    type = do['type']
    data = do['data']

    if type == 'press':
        presserAppend(data)
    elif type == 'lcd':
        updateLCDFromJobData(data)
    else:
        raise Exception(f"Invalid Job Type '{do}'")

