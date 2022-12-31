import json
from flask import request, Blueprint, current_app, jsonify
from flask_expects_json import expects_json

from smart_home_server.api import postLCDSchema
from smart_home_server.threads.lcd import toggleLCDBacklight, updateLCDFromJobData

from smart_home_server.notes import getNote, deleteNote, updateNote, createNote, NoteAlreadyExists, NoteDoesNotExist

dashboardApi = Blueprint('dashboardApi', __name__)

@dashboardApi.route('/api/dashboard/lcd', methods=['POST'])
@expects_json(postLCDSchema, check_formats=True)
def postLCDRoute():
    data = json.loads(request.data)
    if not updateLCDFromJobData(data):
        return current_app.response_class(f"String Must be ASCII", status=400, mimetype="text/plain")
    return current_app.response_class(f"", status=200)


@dashboardApi.route('/api/dashboard/lcd/toggle', methods=['POST'])
def postLCDToggleBacklightRoute():
    toggleLCDBacklight()
    return current_app.response_class(status=200)


#########
# Notes #
#########


_noteNameContent = \
{
    "name": {"type": "string", "minLength": 0, "maxLength": 20, "pattern": "^[^\n\r]*$"}, # defaults to Note
    "content": {"type": "string", "minLength": 0, "maxLength": 1000, "pattern": ""}, # defaults to empty string
}
_noteId = \
{
    "id":  {"type": "string", "minLength": 0, "maxLength": 50, "pattern": "^[^\n\r]*$"}, # defaults to Note
}
postNoteSchema = \
{
    "type": "object",
    "properties": _noteNameContent,
    'additionalProperties': False,
}
patchNoteSchema = \
{
    "type": "object",
    "properties": {
        **_noteId,
        **_noteNameContent
    },
    'required': ['id'],
    'additionalProperties': False,
}
searchNoteSchema = \
{
    "type": "object",
    "properties": _noteId,
    'required': ['id'],
    'additionalProperties': False,
}
deleteNoteSchema = searchNoteSchema

@dashboardApi.route('/api/dashboard/note', methods=['POST'])
@expects_json(postNoteSchema, check_formats=True)
def postNoteRoute():
    data = json.loads(request.data)

    if 'name' not in data or not data['name']:
        name = 'Note'
    else:
        name = data['name']

    content = '' if 'content' not in data else data['content']
    try:
        createNote(name, content)
        return current_app.response_class(status=200)
    except NoteAlreadyExists:
        return current_app.response_class("Note With That ID Already Exists (should never occur)", status=400)

@dashboardApi.route('/api/dashboard/note', methods=['PATCH'])
@expects_json(patchNoteSchema, check_formats=True)
def patchNoteRoute():
    data = json.loads(request.data)
    id = data['id']

    if 'name' not in data or not data['name']:
        name = None
    else:
        name = data['name']

    content = None if 'content' not in data else data['content']
    try:
        updateNote(id, name = name, content = content)
        return current_app.response_class(status=200)
    except NoteDoesNotExist:
        return current_app.response_class(f"Note with ID:{id} Does Not Exist", status=400)

@dashboardApi.route('/api/dashboard/note', methods=['SEARCH'])
@expects_json(searchNoteSchema, check_formats=True)
def searchNoteRoute():
    data = json.loads(request.data)
    id = data['id']
    try:
        note = getNote(id)
        return jsonify(note)
    except NoteDoesNotExist:
        return current_app.response_class(f"Note with ID:{id} Does Not Exist", status=400)

@dashboardApi.route('/api/dashboard/note', methods=['DELETE'])
@expects_json(deleteNoteSchema, check_formats=True)
def deleteNoteRoute():
    data = json.loads(request.data)
    id = data['id']
    try:
        deleteNote(id)
        return current_app.response_class(status=200)
    except NoteDoesNotExist:
        return current_app.response_class(f"Note with ID:{id} Does Not Exist", status=400)


