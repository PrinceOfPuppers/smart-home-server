from uuid import uuid4
import os
import json
import smart_home_server.constants as const

class NoteDoesNotExist(Exception):
    pass

class NoteAlreadyExists(Exception):
    pass

def _getNotePath(id:str):
    return f'{const.noteFolder}/{id}'

def _createNote(name:str, content:str, id=None):
    if id == None:
        id = str(uuid4())

    path = _getNotePath(id)
    if os.path.exists(path):
        raise NoteAlreadyExists()

    name = name.replace('\n', ' ').strip()
    content = content.strip()
    with open(path, "w") as f:
        f.write(json.dumps({"name":name, "content":content}))


def _deleteNote(id: str):
    path = _getNotePath(id)
    if os.path.exists(path):
        os.remove(path)
        return
    raise NoteDoesNotExist()

def _updateNote(id:str, name:str=None, content:str=None):
    note = _getNote(id)
    if note is None:
        return NoteDoesNotExist()
    name = note['name'] if name is None else name
    content = note['content'] if content is None else content
    _deleteNote(id)
    _createNote(name,content, id=id)


def _getNote(id:str):
    path = _getNotePath(id)
    if not os.path.exists(path):
        raise NoteDoesNotExist()

    with open(path, "r") as f:
        j = json.loads(f.read())

    j['id'] = id
    return j

def _getNotes():
    dir = os.listdir(const.noteFolder)
    notes = []
    for id in dir:
        note = _getNote(id)
        if note is None:
            continue
        notes.append(note)
    return notes
