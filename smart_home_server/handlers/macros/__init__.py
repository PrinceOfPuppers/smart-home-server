from threading import Lock
import os

from smart_home_server.handlers.macros.helpers import MacroAlreadyExists, MacroDoesNotExist, SequenceItemDoesNotExist, \
                                                     _getMacro, _getMacros, _deleteMacro, _updateMacroName, _overwriteMacro, _saveMacro, \
                                                     _deleteMacroSequenceItem, _addMacroSequenceItem, _getMacroPath, _addCodeToMacro, _getMacroWithCode, _deleteMacroCode

_macroLock = Lock()


def saveMacro(macro:dict, id=None):
    with _macroLock:
        _saveMacro(macro, id=id)


def deleteMacro(id: str):
    with _macroLock:
        _deleteMacro(id)

def overwriteMacro(id:str, newMacro:dict):
    with _macroLock:
        _overwriteMacro(id, newMacro)

def getMacro(id:str):
    with _macroLock:
        return _getMacro(id)

def getMacros():
    with _macroLock:
        return _getMacros()

def addMacroSequenceItem(id, sequenceItem, index = -1):
    with _macroLock:
        _addMacroSequenceItem(id, sequenceItem, index=index)


def deleteMacroSequenceItem(macroId, sequenceItemId):
    with _macroLock:
        _deleteMacroSequenceItem(macroId, sequenceItemId)

def updateMacroName(id, name):
    with _macroLock:
        _updateMacroName(id, name)

def macroExists(id):
    path = _getMacroPath(id)
    if os.path.exists(path):
        return True
    return False

def addCodeToMacro(id, code):
    with _macroLock:
        _addCodeToMacro(id, code)

def deleteMacroCode(id):
    with _macroLock:
        _deleteMacroCode(id)

def getMacroWithCode(code):
    with _macroLock:
        _getMacroWithCode(code)

