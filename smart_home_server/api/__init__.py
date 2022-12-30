import smart_home_server.constants as const
from smart_home_server.threads.presser import presserAppend
from smart_home_server.threads.lcd import updateLCDFromJobData

postRemoteSchema = \
{
    "type": "object",
    "properties": {
        "remote": {"type": "string", "minLength": 0, "maxLength": 20, "pattern": "^[ -~]*$"}, # no default, any ascii string is valid
        "channel": { "type": "integer", "minimum": 0 }, # defaults to 0, validated in function
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

# additional sanatization not done by schema
def validateJob(job:dict):
    try:
        do   = job['do']
        type = do['type']
        data = do['data']

        if type == 'press':
            remote = data['remote']
            ch = data['channel']
            if not remote in const.remotes:
                return False
            max = len(const.remotes[remote]) - 1
            min = 0
            if ch < min or ch > max:
                return f"Invalid Channel: {ch} for Remote: {remote} (min: {min}, max: {max})"

        elif type == 'lcd':
            return ""

        else:
            print(f"Invalid Job Type '{do}'")
            return "Invalid Job Type"
    except:
        return ""
    


def runJob(job:dict):
    # job must contain key 'do'
    if not job['enabled']:
        return

    do   = job['do']
    type = do['type']
    data = do['data']

    if type == 'press':
        presserAppend(data)
    elif type == 'lcd':
        updateLCDFromJobData(data)
    else:
        raise Exception(f"Invalid Job Type '{do}'")

