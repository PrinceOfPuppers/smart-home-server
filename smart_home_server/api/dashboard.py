import json
from flask import request, Blueprint, current_app
from flask_expects_json import expects_json
import requests

from smart_home_server.threads.lcd import startUpdateLCD, getLCDFMT, toggleLCDBacklight
from smart_home_server.helpers import addDefault, getExchangeRate, getForecastStr
import smart_home_server.constants as const


dashboardApi = Blueprint('dashboardApi', __name__)

@dashboardApi.route('/api/dashboard/forex', methods=['GET'])
def getForex():
    src = request.args.get('src', default='usd')
    dest = request.args.get('dest', default='cad')
    try:
        exchangeRate = getExchangeRate(src,dest)
    except:
        return current_app.response_class("Error Scraping Exchange Rate", status=500, mimetype="text/plain")
    if exchangeRate is None:
        return current_app.response_class(f"No Exchange Rate Data Found for {src} to {dest}", status=400, mimetype="text/plain")
    return current_app.response_class(exchangeRate, status=200, mimetype="text/plain")

def wttrIn(url, stripHead, stripTail):
    r = requests.get(url)
    if r.ok:
        return '\n'.join(r.text.split('\n')[stripHead:stripTail])
    else:
        None

@dashboardApi.route('/api/dashboard/large-forecast', methods=['GET'])
def getLargeForecast():
    t = wttrIn(const.forecastUrl, 0, -3)
    if t is None:
        return current_app.response_class(f"Error Getting Forecast", status=400, mimetype="text/plain")
    return current_app.response_class(t, status=200, mimetype="text/plain")

@dashboardApi.route('/api/dashboard/forecast', methods=['GET'])
def getForecast():
    t = getForecastStr(const.wttrApiUrl)
    if t is None:
        return current_app.response_class(f"Error Getting Forecast", status=400, mimetype="text/plain")
    return current_app.response_class(t, status=200, mimetype="text/plain")



@dashboardApi.route('/api/dashboard/weather', methods=['GET'])
def getWeather():
    t = wttrIn(const.weatherUrl,0,-1)
    if t is None:
        return current_app.response_class(f"Error Getting Weather", status=400, mimetype="text/plain")
    return current_app.response_class(t, status=200, mimetype="text/plain")

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
    return current_app.response_class(s, status=200, mimetype="text/plain")

@dashboardApi.route('/api/dashboard/lcd/toggle', methods=['POST'])
def postLCDToggleBacklight():
    s = toggleLCDBacklight()
    return current_app.response_class(s, status=200, mimetype="text/plain")
