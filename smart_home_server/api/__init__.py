import json
from flask import jsonify, request, Blueprint, current_app
from flask_expects_json import expects_json

import smart_home_server.constants as const
from smart_home_server.threads.scheduler import addJob, removeJob, getJobs, enableDisableJob
from smart_home_server.threads.presser import presserAppend

api = Blueprint('api', __name__)

remotePressSchema = \
{
    "type": "object",
    "properties": {
        "channel": { "type": "integer", "minimum": 0, "maximum": len(const.txChannels)-1}, # defaults to 0
        "value": { "type": "boolean" } # defaults to True
    },
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
    "required": ["presses"]
}

@api.route('/api/remote', methods=['POST'])
@expects_json(remoteSchema)
def changeLights():
    presses = json.loads(request.data)['presses']

    for press in presses:
        press['channel'] = 0 if 'channel' not in press else press['channel']
        press['value'] = True if 'value' not in press else press['value']
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
    "required": ["type", "data"]
}

postJobSchema = \
{
    "type": "object",
    "properties":{
        "name":      {"type": "string"},
        #"id":        {"type": "string"},
        "enabled":   {"type": "boolean"}, # defaults to True
        "every":     {"type": "integer"},
        "unit":      {"enum": ["second", "seconds", "minute", "minutes", "hour", "hours", "day", "days", "week", "weeks",
                               "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
                     ]},
        "at":        {"type": "string"},
        "do": {
            "oneOf": [remotePressAction]},
    },
    "required": ['name', "unit", 'do']
}

@api.route('/api/schedule', methods=['POST'])
@expects_json(postJobSchema, check_formats=True)
def postJob():
    print("here")
    scheduledJob = json.loads(request.data)
    scheduledJob['enabled'] = True if 'enabled' not in scheduledJob else scheduledJob['enabled']
    addJob(scheduledJob)
    return current_app.response_class(status=200)


deleteJobSchema = \
{
        "type": "object",
        "properties": {
            "id": {"type": "string"}
        },
        "required": ["id"]
}

@api.route('/api/schedule/jobs', methods=['DELETE'])
@expects_json(deleteJobSchema)
def deleteJob():
    id = json.loads(request.data)['id']
    removeJob(id)
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
    "required": ['id']
}

@api.route('/api/schedule/jobs/enable', methods=['PUT'])
@expects_json(enableJobSchema)
def enableJob():
    data = json.loads(request.data)
    data['enable'] = True if 'enable' not in data else data['enable']
    enableDisableJob(data['id'], data['enable'])
    return current_app.response_class(status=200)

@api.route('/api/test', methods=['GET'])
def test():
    return jsonify({"hi": "there"})
