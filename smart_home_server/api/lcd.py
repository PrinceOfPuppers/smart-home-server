import json
from flask import request, Blueprint, current_app
from flask_expects_json import expects_json

from smart_home_server.handlers.lcd import overwriteLcd, saveLcd, deleteLcd, LcdDoesNotExist, LcdAlreadyExists

from smart_home_server.handlers.logs import logs

from smart_home_server.api import nameSchema, patchLcdSchema
import smart_home_server.constants as const

dashboardApi = Blueprint('dashboardApi', __name__)


postLcdSchema = \
{
    "type": "object",
    "properties": {
        "num": { "type": "integer", "minimum": 0 },
        "name": nameSchema, # defaults to New Lcd
    },
    "required": ["num"],
    'additionalProperties': False,
}

deleteLcdSchema = \
{
    "type": "object",
    "properties": {
        "num": { "type": "integer", "minimum": 0 },
    },
    "required": ["num"],
    'additionalProperties': False,
}

@dashboardApi.route('/api/lcd', methods=['POST'])
@expects_json(postLcdSchema, check_formats=True)
def postLCDRoute():
    data = json.loads(request.data)
    try:
        saveLcd(data["num"], data)
    except LcdAlreadyExists:
        return current_app.response_class(f"Lcd {data["num"]} Already Exists", status=400, mimetype="text/plain")
    return current_app.response_class(f"", status=200)

@dashboardApi.route('/api/lcd', methods=['PATCH'])
@expects_json(patchLcdSchema, check_formats=True)
def patchLCDRoute():
    data = json.loads(request.data)

    try:
        overwriteLcd(data["num"], data)

    except LcdDoesNotExist:
        return current_app.response_class(f"Lcd {data["num"]} Does Not Exist Exists", status=400, mimetype="text/plain")
    return current_app.response_class(f"", status=200)

@dashboardApi.route('/api/lcd', methods=['DELETE'])
@expects_json(deleteLcdSchema, check_formats=True)
def deleteLCDRoute():
    data = json.loads(request.data)

    try:
        deleteLcd(data["num"])

    except LcdDoesNotExist:
        return current_app.response_class(f"Lcd {data["num"]} Does Not Exist Exists", status=400, mimetype="text/plain")
    return current_app.response_class(f"", status=200)

