import smart_home_server.constants as const
from smart_home_server.threads.presser import presserAppend

remotePressSchema = \
{
    "type": "object",
    "properties": {
        "channel": { "type": "integer", "minimum": 0, "maximum": len(const.txChannels)-1}, # defaults to 0
        "value": { "type": "boolean" } # defaults to True
    },
    'additionalProperties': False,
}

remotePressAction = \
{
    "type": "object",
    "properties": {
        "type": {"const":"press"},
        "data": remotePressSchema,
    },
    "required": ["type", "data"],
    'additionalProperties': False,
}


allJobsSchema = [remotePressAction]


def runJob(job:dict):
    # job must contain key 'do'
    do = job['do']
    if do['type'] == 'press':
        presserAppend(do['data'])
    else:
        raise Exception(f"Invalid Job Type '{do}'")
