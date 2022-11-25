import json
from flask import request, Blueprint, current_app, jsonify
from flask_expects_json import expects_json
import requests

from smart_home_server.threads.lcd import startUpdateLCD, getLCDFMT, toggleLCDBacklight
from smart_home_server.hardware_interfaces.dht22 import getDHT
from smart_home_server.helpers import addDefault, getExchangeRate, getWttrForecast
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
    res = {
        'str': str(exchangeRate),
        'data': {
            'src': src,
            'dest': dest,
            'rate': exchangeRate,
        },
        'pollingPeriod': 5*60,
    }
    return jsonify(res)

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

    res = {
        'str': t,
        'data': {},
        'pollingPeriod': 10*60
    }
    return jsonify(res)

@dashboardApi.route('/api/dashboard/forecast', methods=['GET'])
def getForecast():
    t = getWttrForecast(const.wttrApiUrl)
    if t is None:
        return current_app.response_class(f"Error Getting Forecast", status=400, mimetype="text/plain")
    s, data = t
    res = {
        'str': s,
        'data': data,
        'pollingPeriod': 10*60
    }
    return jsonify(res)



@dashboardApi.route('/api/dashboard/weather-image', methods=['GET'])
def getWeather():
    s = wttrIn(const.weatherUrl,0,-1)
    if s is None:
        return current_app.response_class(f"Error Getting Weather", status=400, mimetype="text/plain")
    res = {
        'str': s,
        'data': {},
        'pollingPeriod': 10*60,
    }
    return jsonify(res)

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

@dashboardApi.route('/api/dashboard/temp-humid', methods=['GET'])
def getTempHumid():
    data = getDHT()
    if data is None:
        s = f'Temprature: N/A \nHumidity: N/A'
        res = {
            'str':s,
            'data':{},
            'pollingPeriod': 31,
        }
    else:
        s = f'Temprature: {data.temp} \nHumidity: {data.humid}'
        res = {
            'str':s,
            'data':{'temp':data.temp, 'humid': data.humid},
            'pollingPeriod': 31,
        }
    return jsonify(res)










