import json
from flask import request, Blueprint, current_app
from flask_expects_json import expects_json

from smart_home_server.handlers.logs import logs
from smart_home_server.errors import clearAllErrors

from smart_home_server.api.schemaTypes import nameSchema

dashboardApi = Blueprint('dashboardApi', __name__)

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

@dashboardApi.route('/api/dashboard/errors', methods=['DELETE'])
def deleteErrorsRoute():
    clearAllErrors()
    return current_app.response_class(status=200)

