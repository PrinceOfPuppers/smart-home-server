from threading import Lock

from smart_home_server.handlers.notes.helpers import _createNote, _deleteNote, _updateNote, _getNote, _getNotes, \
                                                     NoteAlreadyExists, NoteDoesNotExist

_noteLock = Lock()

def createNote(name:str, content:str, id=None):
    with _noteLock:
        _createNote(name, content, id=id)


def deleteNote(id: str):
    with _noteLock:
        _deleteNote(id)

def updateNote(id:str, name=None, content=None):
    with _noteLock:
        _updateNote(id, name=name, content=content)

def getNote(id:str):
    with _noteLock:
        return _getNote(id)

def getNotes():
    with _noteLock:
        return _getNotes()
