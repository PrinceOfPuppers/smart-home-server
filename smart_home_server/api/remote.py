import json
from flask import request, Blueprint, current_app
from flask_expects_json import expects_json

from smart_home_server.helpers import addDefault
from smart_home_server.threads.presser import presserAppend

from smart_home_server.api import remotePressSchema

remoteApi = Blueprint('remoteApi', __name__)

remoteSchema = \
{
    "type": "object",
    "properties": {
        "presses": {
            "type": "array",
            "minItems": 1,
            "items": remotePressSchema
        }
    },
    "required": ["presses"],
    'additionalProperties': False,
}

@remoteApi.route('/api/remote', methods=['POST'])
@expects_json(remoteSchema)
def changeLights():
    presses = json.loads(request.data)['presses']

    for press in presses:
        addDefault(press, 'channel', 0)
        addDefault(press, 'value', True)
        presserAppend(press)

    return current_app.response_class(status=200)

