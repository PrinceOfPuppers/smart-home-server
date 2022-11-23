import json
from flask import request, Blueprint, current_app
from flask_expects_json import expects_json
import requests

from smart_home_server.helpers import addDefault, getExchangeRate
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

@dashboardApi.route('/api/dashboard/forcast', methods=['GET'])
def getForcast():
    t = wttrIn(const.forcastUrl, 0, -3)
    if t is None:
        return current_app.response_class(f"Error Getting Forcast", status=400, mimetype="text/plain")
    return current_app.response_class(t, status=200, mimetype="text/plain")


@dashboardApi.route('/api/dashboard/weather', methods=['GET'])
def getWeather():
    t = wttrIn(const.weatherUrl,0,-1)
    if t is None:
        return current_app.response_class(f"Error Getting Weather", status=400, mimetype="text/plain")
    return current_app.response_class(t, status=200, mimetype="text/plain")

