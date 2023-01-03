import json
from flask import jsonify, request, Blueprint, current_app
from flask_expects_json import expects_json
import copy

from smart_home_server.handlers.scheduler import addJob, removeJob, getJobs, enableDisableJob, updateJobName, getJob, JobDoesNotExist
from smart_home_server.helpers import getAtTime, addDefault

from smart_home_server.api import allJobsSchema, validateJob, nameSchema, idSchema, patchNameSchema

scheduleApi = Blueprint('scheduleApi', __name__)

weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
timeUnits = ["second", "minute", "hour", "day", "week"] + weekdays

postScheduledJobSchema = \
{
    "type": "object",
    "properties":{
        "name":      nameSchema,
        #"id":        {"type": "string"},
        "enabled":   {"type": "boolean"}, # defaults to True
        "every":     {"type": "integer"},
        "unit":      {"enum": timeUnits},
        #"at":        {"type": "string"},
        "atSeconds": {"type": "integer", "minimum": 0, "maximum": 59},
        "atMinutes": {"type": "integer", "minimum": 0, "maximum": 59},
        "atHours":   {"type": "integer", "minimum": 0, "maximum": 23},

        "do": {"oneOf": allJobsSchema},
    },
    "required": ['name', "unit", 'do'],
    'additionalProperties': False,
}

deleteJobSchema = \
{
    "type": "object",
    "properties": {
        "id": idSchema
    },
    "required": ["id"],
    'additionalProperties': False,
}

enableJobSchema = \
{
    "type": "object",
    "properties": {
        "id": idSchema,
        "enable": {"type": "boolean"} # defaults to True
    },
    "required": ['id'],
    'additionalProperties': False,
}


@scheduleApi.route('/api/schedule', methods=['POST'])
@expects_json(postScheduledJobSchema, check_formats=True)
def postJob():
    data = json.loads(request.data)
    addDefault(data, 'enabled', True)

    if 'every' in data:
        if data['every'] > 1:
            if data['unit'] in weekdays:
                return current_app.response_class("days of the week 'units' are incompatible with 'every' > 1", status=400)
        else:
            data.pop('every')

    atTime = getAtTime(data)
    if atTime is not None:
        data['at'] = atTime

    if 'at' in data and data['unit'] == 'week':
        return current_app.response_class("unit week is incompatible at times", status=400)

    data.pop('atHours', None)
    data.pop('atMinutes', None)
    data.pop('atSeconds', None)

    
    invalid = validateJob(data)
    if invalid:
        return current_app.response_class(invalid, status=400)

    addJob(data)
    return current_app.response_class(status=200)


@scheduleApi.route('/api/schedule/jobs', methods=['DELETE'])
@expects_json(deleteJobSchema)
def deleteJob():
    data = json.loads(request.data)
    id = data['id']
    removeJob(id)
    return current_app.response_class(status=200)


@scheduleApi.route('/api/schedule/jobs', methods=['PATCH'])
@expects_json(patchNameSchema)
def patchJob():
    patch = json.loads(request.data)
    addDefault(patch, 'name', 'job')
    id = patch['id']
    name = patch['name']

    try:
        updateJobName(id, name)
    except JobDoesNotExist:
        return current_app.response_class(f"ID: {id} Does Not Exist", status=400)
    except Exception:
        return current_app.response_class(status=400)
    return current_app.response_class(status=200)

@scheduleApi.route('/api/schedule/jobs', methods=['GET'])
def GetJobs():
    jobs = getJobs()
    return jsonify({"jobs": jobs})

@scheduleApi.route('/api/schedule/jobs/enable', methods=['POST'])
@expects_json(enableJobSchema)
def enableJob():
    data = json.loads(request.data)
    addDefault(data, 'enabled', True)
    enableDisableJob(data['id'], data['enable'])
    return current_app.response_class(status=200)

