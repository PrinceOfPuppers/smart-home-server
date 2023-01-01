import json
from flask import request, Blueprint, current_app, jsonify
from flask_expects_json import expects_json

from smart_home_server.api import allJobsSchema, nameSchema, idSchema

from smart_home_server.macros import getMacro, saveMacro, addMacroSequenceItem, deleteMacro, runMacro, deleteMacroSequenceItem, \
                                     MacroAlreadyExists, MacroDoesNotExist, SequenceItemDoesNotExist

macroApi = Blueprint('macroApi', __name__)

postDelaySchema = {
    {
        "type": "object",
        "properties": {
            "seconds": { "type": "integer", "minimum": 0, "maximum": 60*60*24}, # defaults to 0
            "minutes": { "type": "integer", "minimum": 0, "maximum": 60*24 },   # defaults to 0
            "hours":   { "type": "integer", "minimum": 0, "maximum": 24},       # defaults to 0
        },
        "required": [],
        'additionalProperties': False,
    }
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
    {
        "type": "object",
        "properties": {
            "type": {"const": "job"},
            "data": {"enum": allJobsSchema},
        },
        "required": ["type", "data"],
        'additionalProperties': False,
    }, 
]

postMacroSequenceSchema = \
{
    "type": "array",
    "items": {
        "enum": macroSequenceItemSchema
    },
    'additionalProperties': False,
}
postMacroSchema = \
{
        "type": "object",
        "properties": {
            "name":     nameSchema, # defaults to Macro if empty
            "sequence": postMacroSequenceSchema,
        },
        "required": ["sequence", "name"],
        'additionalProperties': False,
}
addMacroSequenceItemSchema = \
{
    "type": "object",
    "properties": {
        "id":   idSchema,
        "index": { "type": "integer", "minimum": -1 }, #defaults to -1, validated in function
        "item": macroSequenceItemSchema,
    },
    'required': ['id', 'item'],
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

@macroApi.route('/api/macro', methods=['POST'])
@expects_json(postMacroSchema, check_formats=True)
def postMacroRoute():
    data = json.loads(request.data)
    try:
        saveMacro({"name": data['name'], "sequence": data['sequence']})
        return current_app.response_class(status=200)
    except MacroAlreadyExists:
        return current_app.response_class("Macro With That ID Already Exists (should never occur)", status=400)
    except:
        return current_app.response_class(status=400)

@macroApi.route('/api/macro/item', methods=['PATCH'])
@expects_json(addMacroSequenceItemSchema, check_formats=True)
def addMacroSequenceItemRoute():
    data = json.loads(request.data)
    id = data['id']
    index = -1 if not 'index' in data else data['index']
    item = data['item']
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

