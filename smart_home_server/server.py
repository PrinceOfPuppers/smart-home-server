import json
from flask import Flask, jsonify, request
from flask_expects_json import expects_json

import smart_home_server.constants as const
from smart_home_server.threads.scheduler import startScheduler, stopScheduler, joinScheduler, addJob, removeJob, getJobs
from smart_home_server.threads.presser import startPresser, stopPresser, joinPresser, presserAppend
from smart_home_server import InterruptTriggered

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


#input tasks will not have an id
{
    "name": "test job",
    "id": "asdfakhjfqkhlk",
    "enabled": True,
    "every": 2,
    "unit": "hours",
    "at": "HH:MM:SS",

    "do": {
        "type": "press",
        "data": {
            "channel": 1,
            "value": False
        }

    }
}

lightPressAction = \
{
    "type": "object", 
    "properties": {
        "type": {"const":"press"}, 
        "data": {lightPressSchema}
    },
    "required": ["type", "data"]
}

postJobSchema = \
{
    "type": "object",
    "properties":{
        "name":      {"type": "string"},
        #"id":        {"type": "string"},
        "enabled":   {"type": "bool", "default": True},
        "every":     {"type": "integer"},
        "unit":      {"enum": ["second", "seconds", "minuite", "minuites", "hour", "hours", "day", "days", "week", "weeks",
                               "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
                     ]},
        "at":        {"type": "string", "format": "time"},
        "do": {
            "oneOf": [lightPressAction]},
    },
    "required": ['name', "unit", 'do']
}

@app.route('/schedule', methods=['POST'])
@expects_json(postJobSchema, fill_defaults=True, check_formats=True)
def postJob():
    scheduledJob = json.loads(request.data)
    addJob(scheduledJob)
    return app.response_class(status=200)


deleteJobSchema = \
{
        "type": "object",
        "properties": {
            "id": {"type": "string"}
        },
        "required": ["id"]
}

@app.route('/schedule/jobs', methods=['DELETE'])
@expects_json(deleteJobSchema)
def deleteJob():
    id = json.loads(request.data)['id']
    removeJob(id)
    return app.response_class(status=200)


@app.route('/schedule/jobs', methods=['GET'])
def GetJobs():
    jobs = getJobs()
    return jsonify({"jobs": jobs})


enableJobSchema = \
{
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "enable": {"type": "boolean", "default": True}
    },
    "required": ['id']
}

@app.route('/schedule/jobs/enable', methods=['PUT'])
@expects_json(enableJobSchema, fill_defaults=True)
def enableJob():
    jobs = getJobs()
    return jsonify({"jobs": jobs})

def startServer():
    global app
    try:
        startPresser()
        startScheduler()
        app.run()
    except InterruptTriggered:
        stopPresser()
        stopScheduler()
        joinPresser()
        joinScheduler()

if __name__ == '__main__':
    startServer()
