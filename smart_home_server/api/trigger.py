import json
from flask import jsonify, request, Blueprint, current_app
from flask_expects_json import expects_json

from smart_home_server.helpers import addDefault
from smart_home_server.data_sources import dataSourceValues
from smart_home_server.threads.triggerManager import addTrigger, updateTriggerName, removeTrigger, enableDisableTrigger, getTrigger, getTriggers

from smart_home_server.api import allJobsSchema, validateJob, nameSchema, idSchema

triggerApi = Blueprint('triggerApi', __name__)

triggerComparisons = ['>', '<', '=', '>=', '<=', 'contains']

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
        "name":      nameSchema,
        "enabled":   {"type": "boolean"}, # defaults to True
        'negated':   {"type": "boolean"}, # defaults to false
        'firstVar':  dataSourceSchema,
        'comparison': {"enum": triggerComparisons},
        'secondVar':  varSchema,

        "do": {
            "oneOf": allJobsSchema},
    },
    "required": ['name','firstVar', 'comparison', "secondVar", 'do'],
    'additionalProperties': False,
}


@triggerApi.route('/api/trigger', methods=['POST'])
@expects_json(postTriggerSchema, check_formats=True)
def postJob():
    triggeredJob = json.loads(request.data)
    addDefault(triggeredJob, 'negated', False)
    addDefault(triggeredJob, 'enabled', True)

    firstVar = triggeredJob['firstVar']
    if firstVar['value'] not in dataSourceValues:
        return current_app.response_class(f"Unknown Data Value: {firstVar['value']}", status=400)

    secondVar = triggeredJob['secondVar']
    if secondVar['type'] == 'dataSource' and secondVar['value'] not in dataSourceValues:
        return current_app.response_class(f"Unknown Data Value: {secondVar['value']}", status=400)


    invalid = validateJob(triggeredJob)
    if invalid:
        return current_app.response_class(invalid, status=400)
    addTrigger(triggeredJob)
    return current_app.response_class(status=200)


deleteTriggerSchema = \
{
    "type": "object",
    "properties": {
        "id": idSchema
    },
    "required": ["id"],
    'additionalProperties': False,
}

@triggerApi.route('/api/trigger/jobs', methods=['DELETE'])
@expects_json(deleteTriggerSchema)
def deleteTrigger():
    id = json.loads(request.data)['id']
    removeTrigger(id)
    return current_app.response_class(status=200)


# currently only updates name
patchTriggerSchema = \
{
    "type": "object",
    "properties":{
        "id":        idSchema,
        "name":      nameSchema,
    },
    "required": ['id', 'name'],
    'additionalProperties': False,
}
@triggerApi.route('/api/trigger/jobs', methods=['PATCH'])
@expects_json(patchTriggerSchema)
def patchTrigger():
    id = json.loads(request.data)['id']
    name = json.loads(request.data)['name']

    oldTriggeredJob = getTrigger(id)
    if oldTriggeredJob is None:
        return current_app.response_class(f"Triggered Job with ID: {id} Does Not Exist", status=400)

    if oldTriggeredJob['name'] == name:
        return current_app.response_class(status=200)

    updateTriggerName(id, name)
    return current_app.response_class(status=200)

@triggerApi.route('/api/trigger/jobs', methods=['GET'])
def GetTriggers():
    triggers = getTriggers()
    return jsonify({"jobs": triggers})


enableTriggerSchema = \
{
    "type": "object",
    "properties": {
        "id": idSchema,
        "enable": {"type": "boolean"} # defaults to True
    },
    "required": ['id'],
    'additionalProperties': False,
}

@triggerApi.route('/api/trigger/jobs/enable', methods=['POST'])
@expects_json(enableTriggerSchema)
def enableTrigger():
    data = json.loads(request.data)
    addDefault(data, 'enabled', True)
    enableDisableTrigger(data['id'], data['enable'])
    return current_app.response_class(status=200)

