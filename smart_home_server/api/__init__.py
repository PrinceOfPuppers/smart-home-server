import smart_home_server.constants as const
from smart_home_server.handlers.presser import presserAppend
from smart_home_server.handlers.lcd import updateLCDFromJobData
from smart_home_server.hardware_interfaces.reboot import reboot

nameSchema = {"type": "string", "minLength": 0, "maxLength": 20, "pattern": "^[^\n\r]*$"}
idSchema   = {"type": "string", "minLength": 0, "maxLength": 50, "pattern": "^[^\n\r]*$"}

postRemoteSchema = \
{
    "type": "object",
    "properties": {
        "remote": {"type": "string", "minLength": 0, "maxLength": 20, "pattern": "^[ -~]*$"}, # no default, any ascii string is valid
        "channel": { "type": "integer", "minimum": 0 }, # defaults to 0, validated in function
        "value": { "type": "boolean" } # defaults to True
    },
    "required": ['remote'],
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

_schemas = [
    ('press', postRemoteSchema),
    ('lcd', postLCDSchema),
    ('reboot', rebootSchema),
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
def validateDo(do:dict):
    try:
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
        elif type == 'reboot':
            return ""
        elif type == 'lcd':
            return ""
        elif type == 'delay':
            return ""
        else:
            print(f"Invalid Job Type '{do}'")
            return "Invalid Job Type"
    except:
        return "Invalid Job"

def validateJob(job:dict):
    # adds additional sanatization not done by schema
    if not 'do' in job:
        return "Job Must Contain 'do'"
    return validateDo(job['do'])

    


def runJob(job:dict):
    # job must contain key 'do'
    if 'enabled' in job and not job['enabled']:
        return

    do   = job['do']
    type = do['type']
    data = do['data']

    if type == 'press':
        presserAppend(data)
    elif type == 'lcd':
        updateLCDFromJobData(data)
    elif type == 'reboot':
        reboot()
    else:
        raise Exception(f"Invalid Job Type '{do}'")

