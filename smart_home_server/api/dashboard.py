import json
from flask import request, Blueprint, current_app
from flask_expects_json import expects_json

from smart_home_server.api import postLCDSchema
from smart_home_server.handlers.lcd import toggleLCDBacklight, updateLCDFromJobData
from smart_home_server.handlers.logs import logs

from smart_home_server.api import nameSchema 

dashboardApi = Blueprint('dashboardApi', __name__)

@dashboardApi.route('/api/dashboard/lcd', methods=['POST'])
@expects_json(postLCDSchema, check_formats=True)
def postLCDRoute():
    data = json.loads(request.data)
    if not updateLCDFromJobData(data):
        return current_app.response_class(f"String Must be ASCII", status=400, mimetype="text/plain")
    return current_app.response_class(f"", status=200)


@dashboardApi.route('/api/dashboard/lcd/toggle', methods=['POST'])
def postLCDToggleBacklightRoute():
    toggleLCDBacklight()
    return current_app.response_class(status=200)


deleteLogsSchema = \
{
    "type": "object",
    "properties": {
        "name": nameSchema,
    },
    "required": ['name'],
    'additionalProperties': False,
}

@dashboardApi.route('/api/dashboard/logs', methods=['DELETE'])
@expects_json(deleteLogsSchema, check_formats=True)
def deleteLogRoute():

    data = json.loads(request.data)
    name = data['name']
    if name not in logs:
        return current_app.response_class(f"No Log Named: {name}", status=400)

    logs[name].clear()
    return current_app.response_class(status=200)

