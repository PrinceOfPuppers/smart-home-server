import json
from flask import request, Blueprint, current_app, jsonify
from flask_expects_json import expects_json


from smart_home_server.api.schemas import allDatasourcesSchema
from smart_home_server.data_sources.datasourceTypes import Datasource

datasourceApi = Blueprint('datasourceApi', __name__)

addDatasourceSchema = \
{
    "type": "object",
    "properties":{
        "datasource": {
            "oneOf": allDatasourcesSchema},
    },
    "required": ['datasource'],
    'additionalProperties': False,
}

@datasourceApi.route('/api/datasource', methods=['POST'])
@expects_json(addDatasourceSchema, check_formats=True)
def addDatasource():
    j = json.loads(request.data)['datasource']
    print(j)
    ds = Datasource.fromJson(j)
    print(ds)

    #addDefault(press, 'channel', 0)
    #addDefault(press, 'value', True)
    #runJob({"do": {"type": "press", "data": press}})

    return current_app.response_class(status=200)


