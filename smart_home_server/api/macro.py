import json
from flask import request, Blueprint, current_app, jsonify
from flask_expects_json import expects_json

from smart_home_server.api import allJobsSchema, nameSchema, idSchema, patchNameSchema
from smart_home_server.handlers import validateDo, runMacro, cancelSkipDelay
from smart_home_server.helpers import addDefault

from smart_home_server.handlers.macros import getMacro, saveMacro, addMacroSequenceItem, deleteMacro, deleteMacroSequenceItem, updateMacroName, \
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

deleteDelaySchema = \
{
    "type": "object",
    "properties": {
        "id": idSchema,
        "cancel": {"type": "boolean"} # defaults to False
    },
    'required': ['id'],
    'additionalProperties': False,
}

@macroApi.route('/api/macro', methods=['POST'])
@expects_json(postMacroSchema, check_formats=True)
def postMacroRoute():
    data = json.loads(request.data)
    addDefault(data, 'sequence', [])
    addDefault(data, 'name', 'Macro', checkCond=True, strip=True)
    sequence=data['sequence']
    name = data['name']

    try:
        for item in sequence:
            invalid = validateDo(item)
            if invalid:
                return current_app.response_class(invalid, status=400)

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
    addDefault(data, 'name', 'Macro', checkCond=True, strip=True)
    name = data['name']

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
    addDefault(data, 'index', -1)
    item = data['do']

    invalid = validateDo(item)
    if invalid:
        return current_app.response_class(invalid, status=400)

    try:
        addMacroSequenceItem(data['id'], item, index=data['index'])
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

@macroApi.route('/api/macro/delay', methods=['DELETE'])
@expects_json(deleteDelaySchema, check_formats=True)
def deleteDelayRoute():
    data = json.loads(request.data)
    addDefault(data, 'cancel', False)
    id = data['id']
    cancel = data['cancel']
    try:
        cancelSkipDelay(id, cancel)
        return current_app.response_class(status=200)
    except:
        return current_app.response_class(status=400)

