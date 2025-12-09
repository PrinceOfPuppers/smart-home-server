import json
from flask import request, Blueprint, current_app, jsonify
from flask_expects_json import expects_json

from smart_home_server.helpers import addDefault
from smart_home_server.handlers import runJob
from smart_home_server.handlers.presser import newRemote, deleteChannel, addChannel, renameRemote, readRemoteCode, deleteRemote, RemoteDoesNotExist, ChannelDoesNotExist

from smart_home_server.api import postRemoteSchema
from smart_home_server.api.schemaTypes import nameSchema, idSchema

postNewRemoteSchema = \
{
    "type": "object",
    "properties": {
        "name": nameSchema,
    },
    "required": [],
    'additionalProperties': False,
}

deleteRemoteSchema = \
{
    "type": "object",
    "properties": {
        "id": idSchema,
    },
    "required": ['id'],
    'additionalProperties': False,
}

patchRemoteNameSchema = \
{
    "type": "object",
    "properties": {
        "id": idSchema,
        "name": nameSchema,
    },
    "required": ['id'],
    'additionalProperties': False,
}

channelCodeSchema = \
{
    "type": "object",
    "properties": {
        "code": { "type": "integer", "minimum": 0 },
        "protocol": { "type": "integer", "minimum": 0 },
        "pulseLength": { "type": "integer", "minimum": 0 },
    },
    "required": ['code', "protocol", "pulseLength"],
    'additionalProperties': False,
}

postAddChannelSchema = \
{
    "type": "object",
    "properties": {
        "id": idSchema,
        "channel": { "type": "integer", "minimum": -1 }, # defaults to -1
        "onCode": channelCodeSchema,
        "offCode": channelCodeSchema,
    },
    "required": ['id', "channel", "onCode", "offCode"],
    'additionalProperties': False,
}

deleteChannelSchema = \
{
    "type": "object",
    "properties": {
        "id": idSchema,
        "channel": { "type": "integer", "minimum": -1 },
    },
    "required": ['id', 'channel'],
    'additionalProperties': False,
}

remoteApi = Blueprint('remoteApi', __name__)

@remoteApi.route('/api/remote', methods=['POST'])
@expects_json(postRemoteSchema)
def changeLights():
    press = json.loads(request.data)

    addDefault(press, 'channel', 0)
    addDefault(press, 'value', True)
    runJob({"do": {"type": "press", "data": press}})

    return current_app.response_class(status=200)


@remoteApi.route('/api/remote/edit', methods=['POST'])
@expects_json(postNewRemoteSchema)
def newRemoteRoute():
    remote = json.loads(request.data)

    addDefault(remote, 'name', 'New Remote')
    try:
        newRemote(remote['name'])
    except Exception:
        return current_app.response_class(status=400)

    return current_app.response_class(status=200)


@remoteApi.route('/api/remote/edit', methods=['DELETE'])
@expects_json(deleteRemoteSchema)
def deleteRemoteRoute():
    values = json.loads(request.data)

    try:
        deleteRemote(values['id'])
    except Exception as e:
        return current_app.response_class(str(e), status=400)

    return current_app.response_class(status=200)

@remoteApi.route('/api/remote/edit', methods=['PATCH'])
@expects_json(patchRemoteNameSchema)
def renameRemoteRoute():
    values = json.loads(request.data)
    addDefault(values, 'name', 'New Remote')

    try:
        renameRemote(values['id'], values['name'])
    except RemoteDoesNotExist:
        return current_app.response_class(f"Remote with ID: {id} Does Not Exist",status=400)
    except Exception as e:
        return current_app.response_class(str(e), status=400)

    return current_app.response_class(status=200)


@remoteApi.route('/api/remote/edit/channels', methods=['POST'])
@expects_json(postAddChannelSchema)
def addChannelRoute():
    data = json.loads(request.data)
    addDefault(data, 'channel', -1)

    id = data['id']
    channel = data['channel']
    onCode = data['onCode']
    offCode = data['offCode']

    try:
        addChannel(id, channel, onCode, offCode)
    except RemoteDoesNotExist:
        return current_app.response_class(f"Remote with ID: {id} Does Not Exist",status=400)
    except ChannelDoesNotExist as e:
        return current_app.response_class(str(e) ,status=400)
    except Exception as e:
        return current_app.response_class(str(e), status=400)

    return current_app.response_class(status=200)

@remoteApi.route('/api/remote/code', methods=['GET'])
def getRemoteCodeRoute():
    try:
        code = readRemoteCode()
        if code is None:
            return current_app.response_class("No Signal Recieved", status=404)
        return jsonify(code)
    except Exception as e:
        return current_app.response_class(str(e), status=400)


@remoteApi.route('/api/remote/edit/channels', methods=['DELETE'])
@expects_json(deleteChannelSchema)
def deleteChannelRoute():
    values = json.loads(request.data)

    try:
        deleteChannel(values['id'], values['channel'])
    except Exception as e:
        return current_app.response_class(str(e), status=400)

    return current_app.response_class(status=200)

