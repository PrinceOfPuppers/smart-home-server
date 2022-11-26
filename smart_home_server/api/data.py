from flask import Blueprint, current_app, jsonify

from smart_home_server.data_sources import dataSources

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


@dataApi.route('/api/data/sources', methods=['GET'])
def getSources():
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

def f(source):
    dash = source['dashboard']
    res = source['local']()
    if res is None:
        return current_app.response_class(f"Error Getting: {dash['name']}", status=400, mimetype="text/plain")
    return jsonify(res)

view_maker = lambda source: (lambda: f(source))
for source in dataSources:
    if 'dashboard' in source: #and source['dashboard']['enabled']:
        #@dataApi.route(source['url'], methods=['GET'])
        endpoint = source['url'].replace('/','')
        dataApi.add_url_rule(source['url'], view_func = view_maker(source), endpoint=endpoint)
