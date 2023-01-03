from uuid import uuid4
import os
import json
from time import sleep
from threading import Thread
import smart_home_server.constants as const
from smart_home_server.api import runJob

class MacroDoesNotExist(Exception):
    pass

class MacroAlreadyExists(Exception):
    pass

class SequenceItemDoesNotExist(Exception):
    pass


def _getMacroPath(id:str):
    return f'{const.macroFolder}/{id}'

def _saveMacro(macro:dict, id=None):
    if id == None:
        id = str(uuid4())

    path = _getMacroPath(id)
    if os.path.exists(path):
        raise MacroAlreadyExists()

    with open(path, "w") as f:
        f.write(json.dumps(macro))


def _deleteMacro(id: str):
    path = _getMacroPath(id)
    if os.path.exists(path):
        os.remove(path)
        return
    raise MacroDoesNotExist()

def _overwriteMacro(id:str, newMacro:dict):
    _deleteMacro(id)
    return _saveMacro(newMacro, id=id)

def _getMacro(id:str):
    path = _getMacroPath(id)
    if not os.path.exists(path):
        raise MacroDoesNotExist()

    with open(path, "r") as f:
        j = json.loads(f.read())

    j['id'] = id
    return j

def _getMacros():
    dir = os.listdir(const.macroFolder)
    macros = []
    for id in dir:
        macro = _getMacro(id)
        if macro is None:
            continue
        macros.append(macro)
    return macros

def _addMacroSequenceItem(id:str, sequenceItem:dict, index = -1):
    '''also adds id to sequenceItem'''
    macro = _getMacro(id)
    sequenceItemId = str(uuid4())
    sequenceItem['id'] = sequenceItemId
    if index == -1:
        macro['sequence'].append(sequenceItem)
    else:
        index = min(max(index,0), len(macro['sequence']))
        macro['sequence'].insert(index, sequenceItem)

    _overwriteMacro(macro['id'], macro)

def _deleteMacroSequenceItem(macroId, sequenceItemId):
    macro = _getMacro(macroId)
    for i,item in enumerate(macro['sequence']):
        if item['id'] == sequenceItemId:
            macro['sequence'].pop(i)
            _overwriteMacro(macro['id'], macro)
            return
    raise SequenceItemDoesNotExist()

def _runMacroSequence(sequence, delay = 0):
    if len(sequence) == 0:
        return
    if delay > 0:
        sleep(delay)
    for i,item in enumerate(sequence):
        if item['type'] == 'delay':
            data = item['data']
            seconds = data['seconds'] + data['minutes']*60 + data['hours']*60*60
            t = Thread(target= lambda: _runMacroSequence(sequence[i+1:], delay = seconds))
            t.start()
            break
        else:
            runJob({'do': item})

def _updateMacroName(id, name):
    macro = _getMacro(id)
    if macro['name'] == name:
        return
    macro['name'] = name
    _overwriteMacro(id, macro)

