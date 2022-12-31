import json
from flask import request, Blueprint, current_app, jsonify
from flask_expects_json import expects_json

from smart_home_server.api import allJobsSchema, nameSchema, idSchema
from smart_home_server.macros import getMacro, createMacro, updateMacro, deleteMacro, MacroAlreadyExists, MacroDoesNotExist, runMacro

macroApi = Blueprint('macroApi', __name__)

postMacroJobsSchema = \
{
    "type": "array",
    "items": {
        "enum": allJobsSchema
    },
    'additionalProperties': False,
}
postMacroSchema = \
{
        "type": "object",
        "properties": {
            "name": nameSchema, # defaults to Macro if empty
            "jobs": postMacroJobsSchema,
        },
        "required": ["jobs", "name"],
        'additionalProperties': False,
}
patchMacroSchema = \
{
    "type": "object",
    "properties": {
        "id": idSchema,
        "name": nameSchema,
        "jobs": postMacroJobsSchema,
    },
    'required': ['id'],
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
    name = 'Macro' if not data['name'] else data['name']
    jobs = data['jobs']
    try:
        createMacro(name, jobs)
        return current_app.response_class(status=200)
    except MacroAlreadyExists:
        return current_app.response_class("Macro With That ID Already Exists (should never occur)", status=400)


@macroApi.route('/api/macro', methods=['PATCH'])
@expects_json(patchMacroSchema, check_formats=True)
def patchMacroRoute():
    data = json.loads(request.data)
    id = data['id']

    if 'name' not in data or not data['name']:
        name = None
    else:
        name = data['name']

    jobs = None if 'jobs' not in data else data['jobs']
    try:
        updateMacro(id, name = name, jobs = jobs)
        return current_app.response_class(status=200)
    except MacroDoesNotExist:
        return current_app.response_class(f"Macro with ID:{id} Does Not Exist", status=400)

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

