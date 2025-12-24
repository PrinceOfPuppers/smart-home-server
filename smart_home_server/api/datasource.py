import json
import smart_home_server.data_sources.datasourceInterface as dsi
from smart_home_server.api.schemaTypes import nameSchema
from flask import request, Blueprint, current_app
from flask_expects_json import expects_json
import traceback

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

patchDatasourceSchema = \
{
    "type": "object",
    "properties":{
        "datasource": dst.Datasource.getSchema(),
        "oldName": nameSchema,
    },
    "required": ['datasource', 'oldName'],
    'additionalProperties': False,
}

deleteDatasourceSchema = \
{
    "type": "object",
    "properties":{
        "name": nameSchema,
    },
    "required": ['name'],
    'additionalProperties': False,
}

def loadDs(dsj):
    try:
        return dst.Datasource.fromjson(dsj), ""
    except dst.InvalidDatasource as e:
        return None, f"Information for datasource is invalid\nReason: {e}"

@datasourceApi.route('/api/datasource', methods=['POST'])
@expects_json(addDatasourceSchema, check_formats=True)
def addDatasource():
    j = json.loads(request.data)['datasource']
    ds, err = loadDs(j)
    if ds is None:
        return current_app.response_class(err, status=400)

    try:
        dsi.datasourcesMutable.appendDatasource(ds)
    except dst.DatasourceAlreadyExists:
        return current_app.response_class(f"Datasource Already Exists: {ds.name}", status=400)
    except dst.UnknownDatasource as _:
        traceback.print_exc()
        print("addDatasource Unknown Datasource")
        return current_app.response_class(f"Attempting to add datasource:{ds.name} resulted in an internal error", status=500)

    return current_app.response_class(status=200)


@datasourceApi.route('/api/datasource', methods=['PATCH'])
@expects_json(patchDatasourceSchema, check_formats=True)
def patchDatasource():
    j = json.loads(request.data)
    oldName = j["oldName"]
    dsj = j["datasource"]
    ds, err = loadDs(dsj)
    if ds is None:
        return current_app.response_class(err, status=400)

    try:
        dsi.datasourcesMutable.editDatasource(oldName, ds)
    except dst.UnknownDatasource as _:
        return current_app.response_class(f"Datasource with old name: {oldName} does not exist", status=400)

    return current_app.response_class(status=200)


@datasourceApi.route('/api/datasource', methods=['DELETE'])
@expects_json(deleteDatasourceSchema, check_formats=True)
def deleteDatasource():
    name = json.loads(request.data)['name']
    # TODO: catch erros, send useful error codes
    try:
        dsi.datasourcesMutable.deleteDatasource(name)
    except dst.UnknownDatasource as _:
        traceback.print_exc()
        print("deleteDatasource Unknown Datasource")
        return current_app.response_class(f"Attempting to delete datasource: {name} resulted in an internal error", status=500)
    return current_app.response_class(status=200)
