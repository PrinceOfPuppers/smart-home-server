import json
from flask import jsonify, request, Blueprint, current_app
from flask_expects_json import expects_json
import copy

from smart_home_server.threads.scheduler import addJob, removeJob, getJobs, enableDisableJob, updateJob, getJob
from smart_home_server.helpers import getAtTime, addDefault

from smart_home_server.api import allJobsSchema

scheduleApi = Blueprint('scheduleApi', __name__)

weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


dataSourceSchema = \
{
    "type": "object", 
    "properties":{
        "value": {"type": "string", "minLength": 1, "maxLength": 50},
    },
    "required": ['value']
}

varSchema = \
{
    "type": "object", 
    "properties":{
        "type":  {"enum": ['constant', 'dataSource']},
        "value": {"oneOf": [
            {"type": "string", "minLength": 1, "maxLength": 50},
            {"type": "number"},
        ]}
    },
    "required": ['type', 'value']
}

postTriggerSchema = \
{
    "type": "object",
    "properties":{
        "name":      {"type": "string", "minLength": 1, "maxLength": 30},
        "enabled":   {"type": "boolean"}, # defaults to True
        'negated':   {"type": "boolean"}, # defaults to false
        'firstVar':  dataSourceSchema,
        'comparison': {"enum": ['>', '<', '=', '>=', '<=', 'contains']},
        'secondVar':  varSchema,

        "do": {
            "oneOf": allJobsSchema},
    },
    "required": ['name',' firstVar', 'comparison', "secondVar", 'do'],
    'additionalProperties': False,
}


@scheduleApi.route('/api/trigger', methods=['POST'])
@expects_json(postTriggerSchema, check_formats=True)
def postJob():
    triggeredJob = json.loads(request.data)
    addDefault(triggeredJob, 'negated', False)
    addDefault(triggeredJob, 'enabled', True)
    # TODO: ensure sources are in datasources
    addTrigger(triggerJob)
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

@scheduleApi.route('/api/schedule/jobs', methods=['DELETE'])
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
        "name":      {"type": "string", "minLength": 1, "maxLength": 30},
    },
    "required": ['id', 'name'],
    'additionalProperties': False,
}
@scheduleApi.route('/api/schedule/jobs', methods=['PATCH'])
@expects_json(patchJobSchema)
def patchJob():
    id = json.loads(request.data)['id']
    name = json.loads(request.data)['name']

    oldJob = getJob(id)
    if oldJob is None:
        return current_app.response_class(f"ID: {id} Does Not Exist", status=400)

    if oldJob['name'] == name:
        return current_app.response_class(status=200)

    newJob = copy.deepcopy(oldJob)

    newJob['name'] = name

    updateJob(id, newJob)
    return current_app.response_class(status=200)

@scheduleApi.route('/api/schedule/jobs', methods=['GET'])
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

@scheduleApi.route('/api/schedule/jobs/enable', methods=['POST'])
@expects_json(enableJobSchema)
def enableJob():
    data = json.loads(request.data)
    addDefault(data, 'enabled', True)
    enableDisableJob(data['id'], data['enable'])
    return current_app.response_class(status=200)

