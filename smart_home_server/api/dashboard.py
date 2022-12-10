import json
from flask import request, Blueprint, current_app
from flask_expects_json import expects_json

from smart_home_server.api import postLCDSchema
from smart_home_server.threads.lcd import toggleLCDBacklight, updateLCDFromJobData


dashboardApi = Blueprint('dashboardApi', __name__)

@dashboardApi.route('/api/dashboard/lcd', methods=['POST'])
@expects_json(postLCDSchema, check_formats=True)
def postLCD():
    data = json.loads(request.data)
    if not updateLCDFromJobData(data):
        return current_app.response_class(f"String Must be ASCII", status=400, mimetype="text/plain")
    return current_app.response_class(f"", status=200)


@dashboardApi.route('/api/dashboard/lcd/toggle', methods=['POST'])
def postLCDToggleBacklight():
    toggleLCDBacklight()
    return current_app.response_class(status=200)

