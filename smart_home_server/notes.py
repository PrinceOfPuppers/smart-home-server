from uuid import uuid4
import os
import json
import smart_home_server.constants as const
from threading import Lock

_noteLock = Lock()

class NoteDoesNotExist(Exception):
    pass

class NoteAlreadyExists(Exception):
    pass

def _getNotePath(id:str):
    return f'{const.noteFolder}/{id}'

def createNote(name:str, content:str, id=None):
    global _noteLock
    try:
        _noteLock.acquire()
        if id == None:
            id = str(uuid4())

        path = _getNotePath(id)
        if os.path.exists(path):
            raise NoteAlreadyExists()

        name = name.replace('\n', ' ').strip()
        content = content.strip()
        with open(path, "w") as f:
            f.write(json.dumps({"name":name, "content":content}))
    finally:
        _noteLock.release()


def deleteNote(id: str):
    global _noteLock
    try:
        _noteLock.acquire()
        path = _getNotePath(id)
        if os.path.exists(path):
            os.remove(path)
            return
        raise NoteDoesNotExist()
    finally:
        _noteLock.release()

def updateNote(id:str, name:str=None, content:str=None):
    note = getNote(id)
    if note is None:
        return NoteDoesNotExist()
    name = note['name'] if name is None else name
    content = note['content'] if content is None else content
    deleteNote(id)
    return createNote(name,content, id=id)

def getNote(id:str):
    global _noteLock
    try:
        _noteLock.acquire()
        path = _getNotePath(id)
        if not os.path.exists(path):
            raise NoteDoesNotExist()

        with open(path, "r") as f:
            j = json.loads(f.read())

        j['id'] = id
        return j
    finally:
        _noteLock.release()

def getNotes():
    dir = os.listdir(const.noteFolder)
    notes = []
    for id in dir:
        note = getNote(id)
        if note is None:
            continue
        notes.append(note)
    return notes
