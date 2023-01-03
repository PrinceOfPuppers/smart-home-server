import json
from flask import request, Blueprint, current_app, jsonify
from flask_expects_json import expects_json

from smart_home_server.api import allJobsSchema, nameSchema, idSchema, patchNameSchema

from smart_home_server.threads.macros import getMacro, saveMacro, addMacroSequenceItem, deleteMacro, runMacro, deleteMacroSequenceItem, updateMacroName, \
                                     MacroAlreadyExists, MacroDoesNotExist, SequenceItemDoesNotExist

macroApi = Blueprint('macroApi', __name__)

postDelaySchema = {
        "type": "object",
        "properties": {
            "seconds": { "type": "integer", "minimum": 0, "maximum": 60*60*24}, # defaults to 0
            "minutes": { "type": "integer", "minimum": 0, "maximum": 60*24 },   # defaults to 0
            "hours":   { "type": "integer", "minimum": 0, "maximum": 24},       # defaults to 0
        },
        "required": [],
        'additionalProperties': False,
}

macroSequenceItemSchema = [
    {
        "type": "object",
        "properties": {
            "type": {"const": "delay"},
            "data": postDelaySchema,
        },
        "required": ["type", "data"],
        'additionalProperties': False,
    }, 
    *allJobsSchema,
]

postMacroSequenceSchema = \
{
    "type": "array",
    "items": {
        "oneOf": macroSequenceItemSchema
    },
    'additionalProperties': False,
}
postMacroSchema = \
{
        "type": "object",
        "properties": {
            "name":     nameSchema, # defaults to Macro if empty
            "sequence": postMacroSequenceSchema, #defaults to empty list
        },
        "required": [],
        'additionalProperties': False,
}
addMacroSequenceItemSchema = \
{
    "type": "object",
    "properties": {
        "id":   idSchema,
        "index": { "type": "integer", "minimum": -1 }, #defaults to -1, validated in function
        "do": {"oneOf": macroSequenceItemSchema}
    },
    'required': ['id', 'do'],
    'additionalProperties': False,
}
deleteItemMacroSchema = \
{
    "type": "object",
    "properties": {
        "id":   idSchema,
        "itemId": idSchema,
    },
    'required': ['id', 'itemId'],
    'additionalProperties': False,
}
searchMacroSchema = \
{
    "type": "object",
    "properties": {"id": idSchema},
    'required': ['id'],
    'additionalProperties': False,
}
deleteMacroSchema = searchMacroSchema
runMacroSchema = searchMacroSchema

def _sanatizeMacroName(data):
    name = 'macro' if not 'name' in data else data['name'].strip()
    if not name:
        name = 'Macro'
    return name

@macroApi.route('/api/macro', methods=['POST'])
@expects_json(postMacroSchema, check_formats=True)
def postMacroRoute():
    data = json.loads(request.data)
    name = _sanatizeMacroName(data)
    try:
        sequence = [] if not 'sequence' in data else data['sequence']
        saveMacro({"name": name, "sequence": sequence})
        return current_app.response_class(status=200)
    except MacroAlreadyExists:
        return current_app.response_class("Macro With That ID Already Exists (should never occur)", status=400)
    except:
        return current_app.response_class(status=400)

@macroApi.route('/api/macro', methods=['PATCH'])
@expects_json(patchNameSchema)
def patchTrigger():
    data = json.loads(request.data)
    id = data['id']
    name = _sanatizeMacroName(data)

    try:
        updateMacroName(id, name)
        return current_app.response_class(status=200)
    except MacroDoesNotExist:
        return current_app.response_class(f"Macro with ID:{id} Does Not Exist", status=400)
    except:
        return current_app.response_class(status=400)

@macroApi.route('/api/macro/item', methods=['POST'])
@expects_json(addMacroSequenceItemSchema, check_formats=True)
def addMacroSequenceItemRoute():
    data = json.loads(request.data)
    id = data['id']
    index = -1 if not 'index' in data else data['index']
    item = data['do']
    try:
        addMacroSequenceItem(id, item, index=index)
        return current_app.response_class(status=200)
    except MacroDoesNotExist:
        return current_app.response_class(f"Macro with ID:{id} Does Not Exist", status=400)
    except:
        return current_app.response_class(status=400)

@macroApi.route('/api/macro/item', methods=['DELETE'])
@expects_json(deleteItemMacroSchema, check_formats=True)
def deleteMacroSequenceItemRoute():
    data = json.loads(request.data)
    id = data['id']
    itemId = data['itemId']
    try:
        deleteMacroSequenceItem(id, itemId)
        return current_app.response_class(status=200)
    except MacroDoesNotExist:
        return current_app.response_class(f"Macro with ID:{id} Does Not Exist", status=400)
    except SequenceItemDoesNotExist:
        return current_app.response_class(f"Macro with ID:{id} Does Not Contain Item with ID: {itemId}", status=400)
    except:
        return current_app.response_class(status=400)

@macroApi.route('/api/macro', methods=['SEARCH'])
@expects_json(searchMacroSchema, check_formats=True)
def searchMacroRoute():
    data = json.loads(request.data)
    id = data['id']
    try:
        macro = getMacro(id)
        return jsonify(macro)
    except MacroDoesNotExist:
        return current_app.response_class(f"Macro with ID:{id} Does Not Exist", status=400)
    except:
        return current_app.response_class(status=400)

@macroApi.route('/api/macro', methods=['DELETE'])
@expects_json(deleteMacroSchema, check_formats=True)
def deleteMacroRoute():
    data = json.loads(request.data)
    id = data['id']
    try:
        deleteMacro(id)
        return current_app.response_class(status=200)
    except MacroDoesNotExist:
        return current_app.response_class(f"Macro with ID:{id} Does Not Exist", status=400)
    except:
        return current_app.response_class(status=400)


@macroApi.route('/api/macro/run', methods=['POST'])
@expects_json(runMacroSchema, check_formats=True)
def runMacroRoute():
    data = json.loads(request.data)
    id = data['id']
    try:
        runMacro(id)
        return current_app.response_class(status=200)
    except MacroDoesNotExist:
        return current_app.response_class(f"Macro with ID:{id} Does Not Exist", status=400)
    except:
        return current_app.response_class(status=400)

