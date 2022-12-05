import json
from flask import request, Blueprint, current_app
from flask_expects_json import expects_json

from smart_home_server.helpers import addDefault
from smart_home_server.threads.presser import presserAppend

from smart_home_server.api import postRemoteSchema

remoteApi = Blueprint('remoteApi', __name__)

@remoteApi.route('/api/remote', methods=['POST'])
@expects_json(postRemoteSchema)
def changeLights():
    press = json.loads(request.data)

    addDefault(press, 'channel', 0)
    addDefault(press, 'value', True)
    presserAppend(press)

    return current_app.response_class(status=200)

