from flask import Blueprint, current_app, jsonify

from smart_home_server.data_sources import dataSources
from smart_home_server.threads.subscribeManager import getOnce

# return format is 
#example = {
#    'data': {
#        "temp": 123,
#        "humid": 123
#    },
#    'str': f'Temprature: 123 \nHumidity: 123'
#    'pollingPeriod': 60*10
#}

dataApi = Blueprint('dataApi', __name__)

def route(source):
    dash = source['dashboard']
    value = f'{source["name"]}-str'
    values = [value]
    x = getOnce(values)
    if isinstance(x, Exception):
        return current_app.response_class(f"Error Getting: {dash['name']}", status=400, mimetype="text/plain")
    return jsonify(x)


view_maker = lambda source: (lambda: route(source))
for source in dataSources:
    if 'dashboard' in source: #and source['dashboard']['enabled']:
        endpoint = source['url'].replace('/','')
        dataApi.add_url_rule(source['url'], view_func = view_maker(source), endpoint=endpoint)
