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

def createNote(name:str, content:str, id=None, lock=True):
    global _noteLock
    try:
        if lock:
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
        if lock:
            _noteLock.release()


def deleteNote(id: str, lock=True):
    global _noteLock
    try:
        if lock:
            _noteLock.acquire()
        path = _getNotePath(id)
        if os.path.exists(path):
            os.remove(path)
            return
        raise NoteDoesNotExist()
    finally:
        if lock:
            _noteLock.release()

def updateNote(id:str, name:str=None, content:str=None):
    _noteLock.acquire()
    try:
        note = getNote(id, lock=False)
        if note is None:
            return NoteDoesNotExist()
        name = note['name'] if name is None else name
        content = note['content'] if content is None else content
        deleteNote(id, lock=False)
        return createNote(name,content, id=id, lock=False)
    finally:
        _noteLock.release()


def getNote(id:str, lock=True):
    global _noteLock
    try:
        if lock:
            _noteLock.acquire()
        path = _getNotePath(id)
        if not os.path.exists(path):
            raise NoteDoesNotExist()

        with open(path, "r") as f:
            j = json.loads(f.read())

        j['id'] = id
        return j
    finally:
        if lock:
            _noteLock.release()

def getNotes():
    _noteLock.acquire()
    try:
        dir = os.listdir(const.noteFolder)
        notes = []
        for id in dir:
            note = getNote(id, lock=False)
            if note is None:
                continue
            notes.append(note)
        return notes
    finally:
        _noteLock.release()
