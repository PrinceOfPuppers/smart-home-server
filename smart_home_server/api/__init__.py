import json
from flask import jsonify, request, Blueprint, current_app
from flask_expects_json import expects_json
import copy

import smart_home_server.constants as const
from smart_home_server.threads.scheduler import addJob, removeJob, getJobs, enableDisableJob, updateJob, getJob
from smart_home_server.threads.presser import presserAppend
from smart_home_server.helpers import getAtTime, addDefault

api = Blueprint('api', __name__)

remotePressSchema = \
{
    "type": "object",
    "properties": {
        "channel": { "type": "integer", "minimum": 0, "maximum": len(const.txChannels)-1}, # defaults to 0
        "value": { "type": "boolean" } # defaults to True
    },
    'additionalProperties': False,
}

remoteSchema = \
{
    "type": "object",
    "properties": {
        "presses": {
            "type": "array",
            "minItems": 1,
            "items": remotePressSchema
        }
    },
    "required": ["presses"],
    'additionalProperties': False,
}

@api.route('/api/remote', methods=['POST'])
@expects_json(remoteSchema)
def changeLights():
    presses = json.loads(request.data)['presses']

    for press in presses:
        addDefault(press, 'channel', 0)
        addDefault(press, 'value', True)
        presserAppend(press)

    return current_app.response_class(status=200)


#input tasks will not have an id
{
    "name": "test job",
    "id": "asdfakhjfqkhlk",
    "enabled": True,
    "every": 2,
    "unit": "hours",
    "at": "HH:MM:SS",

    "do": {
        "type": "press",
        "data": {
            "channel": 1,
            "value": False
        }

    }
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

weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
postJobSchema = \
{
    "type": "object",
    "properties":{
        "name":      {"type": "string"},
        #"id":        {"type": "string"},
        "enabled":   {"type": "boolean"}, # defaults to True
        "every":     {"type": "integer"},
        "unit":      {"enum": ["second", "minute", "hour", "day", "week"] + weekdays},
        #"at":        {"type": "string"},
        "atSeconds": {"type": "integer", "minimum": 0, "maximum": 59},
        "atMinutes": {"type": "integer", "minimum": 0, "maximum": 59},
        "atHours":   {"type": "integer", "minimum": 0, "maximum": 23},

        "do": {
            "oneOf": [remotePressAction]},
    },
    "required": ['name', "unit", 'do'],
    'additionalProperties': False,
}


@api.route('/api/schedule', methods=['POST'])
@expects_json(postJobSchema, check_formats=True)
def postJob():
    scheduledJob = json.loads(request.data)

    addDefault(scheduledJob, 'enabled', True)
    
    # TODO: return invalid request if every is present with weekday
    if 'every' in scheduledJob:
        if scheduledJob['every'] > 1:
            if scheduledJob['unit'] in weekdays:
                return current_app.response_class("days of the week 'units' are incompatible with 'every' > 1", status=400)
        else:
            scheduledJob.pop('every')

    atTime = getAtTime(scheduledJob)
    if atTime is not None:
        scheduledJob['at'] = atTime

    if 'at' in scheduledJob and scheduledJob['unit'] == 'week':
        return current_app.response_class("unit week is incompatible at times", status=400)

    scheduledJob.pop('atHours', None)
    scheduledJob.pop('atMinutes', None)
    scheduledJob.pop('atSeconds', None)

    addJob(scheduledJob)
    return current_app.response_class(status=200)


deleteJobSchema = \
{
    "type": "object",
    "properties": {
        "id": {"type": "string"}
    },
    "required": ["id"],
    'additionalProperties': False,
}

@api.route('/api/schedule/jobs', methods=['DELETE'])
@expects_json(deleteJobSchema)
def deleteJob():
    id = json.loads(request.data)['id']
    removeJob(id)
    return current_app.response_class(status=200)


# currently only updates name
patchJobSchema = \
{
    "type": "object",
    "properties":{
        "id":        {"type": "string"},
        "name":      {"type": "string"},
    },
    "required": ['id', 'name'],
    'additionalProperties': False,
}
@api.route('/api/schedule/jobs', methods=['PATCH'])
@expects_json(patchJobSchema)
def patchJob():
    id = json.loads(request.data)['id']
    name = json.loads(request.data)['name']

    oldJob = getJob(id)
    newJob = copy.deepcopy(oldJob)

    assert newJob is not None

    newJob['name'] = name

    updateJob(id, newJob)
    return current_app.response_class(status=200)

@api.route('/api/schedule/jobs', methods=['GET'])
def GetJobs():
    jobs = getJobs()
    return jsonify({"jobs": jobs})


enableJobSchema = \
{
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "enable": {"type": "boolean"} # defaults to True
    },
    "required": ['id'],
    'additionalProperties': False,
}

@api.route('/api/schedule/jobs/enable', methods=['POST'])
@expects_json(enableJobSchema)
def enableJob():
    data = json.loads(request.data)
    addDefault(data, 'enabled', True)
    enableDisableJob(data['id'], data['enable'])
    return current_app.response_class(status=200)

@api.route('/api/test', methods=['GET'])
def test():
    return jsonify({"hi": "there"})
