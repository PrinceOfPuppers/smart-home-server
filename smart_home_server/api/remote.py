import json
from flask import request, Blueprint, current_app
from flask_expects_json import expects_json

from smart_home_server.helpers import addDefault
from smart_home_server.handlers import runJob
from smart_home_server.handlers.presser import newRemote, deleteChannel, writeChannelValue, deleteRemote, RemoteDoesNotExist

from smart_home_server.api import postRemoteSchema, nameSchema, idSchema

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

postEditChannelSchema = \
{
    "type": "object",
    "properties": {
        "id": idSchema,
        "channel": { "type": "integer", "minimum": 0 }, # defaults to 0, validated in function
        "value": { "type": "boolean" } # defaults to True
    },
    "required": ['id'],
    'additionalProperties': False,
}

deleteChannelSchema = \
{
    "type": "object",
    "properties": {
        "id": idSchema,
        "channel": { "type": "integer", "minimum": 0 },
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
        newRemote(remote)
    except Exception:
        return current_app.response_class(status=400)

    return current_app.response_class(status=200)


@remoteApi.route('/api/remote/edit', methods=['DELETE'])
@expects_json(deleteRemoteSchema)
def deleteRemoteRoute():
    values = json.loads(request.data)

    try:
        deleteRemote(values['id'])
    except Exception:
        return current_app.response_class(status=400)

    return current_app.response_class(status=200)


@remoteApi.route('/api/remote/edit/channels', methods=['POST'])
@expects_json(postEditChannelSchema)
def writeChannelValueRoute():
    remote = json.loads(request.data)

    addDefault(remote, 'channel', 0)
    addDefault(remote, 'value', True)

    try:
        code = writeChannelValue(remote['id'], remote['channel'], remote['value'])
    except RemoteDoesNotExist:
        return current_app.response_class(f"Remote with ID: {remote['id']} Does Not Exist",status=400)
    except Exception:
        return current_app.response_class(status=400)

    return current_app.response_class(str(code), status=200)


@remoteApi.route('/api/remote/edit/channels', methods=['DELETE'])
@expects_json(deleteChannelSchema)
def deleteChannelRoute():
    values = json.loads(request.data)

    try:
        deleteChannel(values['id'], values['channel'])
    except Exception:
        return current_app.response_class(status=400)

    return current_app.response_class(status=200)

