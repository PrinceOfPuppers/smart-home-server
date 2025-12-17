import json
import smart_home_server.data_sources.datasourceInterface as dsi
from flask import request, Blueprint, current_app, jsonify
from flask_expects_json import expects_json


import smart_home_server.data_sources.datasourceTypes as dst

datasourceApi = Blueprint('datasourceApi', __name__)

addDatasourceSchema = \
{
    "type": "object",
    "properties":{
        "datasource": dst.Datasource.getSchema(),
    },
    "required": ['datasource'],
    'additionalProperties': False,
}

@datasourceApi.route('/api/datasource', methods=['POST'])
@expects_json(addDatasourceSchema, check_formats=True)
def addDatasource():
    j = json.loads(request.data)['datasource']
    print(j)
    ds = dst.Datasource.fromjson(j)
    print(ds)
    # TODO: catch erros, send useful error codes
    dsi.datasourcesMutable.appendDatasource(ds)
    return current_app.response_class(status=200)


