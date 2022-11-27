import json
from flask import request, Blueprint, current_app, jsonify
from flask_expects_json import expects_json

from smart_home_server.threads.lcd import startUpdateLCD, getLCDFMT, toggleLCDBacklight
import smart_home_server.constants as const

# return format is 
#example = {
#    'data': {
#        "temp": 123,
#        "humid": 123
#    },
#    'str': f'Temprature: 123 \nHumidity: 123'
#    'pollingPeriod': 60*10
#}

dashboardApi = Blueprint('dashboardApi', __name__)

postLCDSchema = \
{
    "type": "object",
    "properties": {
        "line1":      {"type": "string", "minLength": 0, "maxLength": 70},
        "line2":      {"type": "string", "minLength": 0, "maxLength": 70},
    },
    "required": ["line1"],
    'additionalProperties': False,
}

@dashboardApi.route('/api/dashboard/lcd', methods=['POST'])
@expects_json(postLCDSchema, check_formats=True)
def postLCD():
    data = json.loads(request.data)
    s = data['line1']
    if 'line2' in data:
        s = f'{s}\n{data["line2"]}'
    try:
        s.encode('ascii')
    except UnicodeEncodeError:
        return current_app.response_class(f"String Must be ASCII", status=400, mimetype="text/plain")

    startUpdateLCD(s)

    return current_app.response_class(f"", status=200)


@dashboardApi.route('/api/dashboard/lcd', methods=['GET'])
def getLCD():
    s = getLCDFMT()
    res = {
        'str': s,
        'data': {},
        'pollingPeriod': 10*60,
    }
    return jsonify(res)

@dashboardApi.route('/api/dashboard/lcd/toggle', methods=['POST'])
def postLCDToggleBacklight():
    toggleLCDBacklight()
    return current_app.response_class(status=200)

