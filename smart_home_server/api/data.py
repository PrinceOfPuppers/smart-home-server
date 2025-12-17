from flask import Blueprint, current_app, jsonify

import smart_home_server.data_sources.datasourceInterface as dsi
import smart_home_server.data_sources.datasourceTypes as dst
from smart_home_server.errors import addSetError, clearErrorInSet

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

def route(source:dst.Datasource):
    res = source.local()

    if not res:
        # add error
        addSetError('Dashboard None', source.name)
        return current_app.response_class(f"Error Getting: {source.name}", status=400, mimetype="text/plain")

    # remove error
    clearErrorInSet('Dashboard None', source.name)
    return jsonify(res)

view_maker = lambda source: (lambda: route(source))
for source in dsi.datasources.datasourceList:
    endpoint = source.url.replace('/','')
    dataApi.add_url_rule(source.url, view_func = view_maker(source), endpoint=endpoint)
