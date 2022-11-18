import json
from flask import Flask, jsonify, request
from flask_expects_json import expects_json

import constants as const
from presser import presserAppend





app = Flask(__name__)

lightPressSchema = \
{
    "type": "object",
    "properties": {
        "channel": { "type": "integer", "minimum": 1, "maximum": const.maxChannels },
        "value": { "type": "boolean" }
    },
    "required": ["channel", "value"]

}

lightsSchema = \
{
    "type": "object",
    "properties": {
        "presses": {
            "type": "array",
            "minItems": 1,
            "items": lightPressSchema
        }
    },
    "required": ["presses"]
}

@app.route('/lights', methods=['POST'])
@expects_json(lightsSchema)
def changeLights():
    presses = json.loads(request.data)['presses']

    for press in presses:
        presserAppend(press)

    return app.response_class(status=200)

app.run()
