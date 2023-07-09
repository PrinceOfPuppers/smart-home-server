from uuid import uuid4
import os
from time import time
import json
from typing import Union

import smart_home_server.constants as const

class MacroDoesNotExist(Exception):
    pass

class MacroAlreadyExists(Exception):
    pass

class SequenceItemDoesNotExist(Exception):
    pass

_macroCache = {}
_rfMacroCodeLastAdded = None

def _getMacroPath(id:str):
    return f'{const.macroFolder}/{id}.json'


def _saveMacro(macro:dict, id=None):
    if id == None:
        id = str(uuid4())
    _macroCache[id] = macro

    path = _getMacroPath(id)
    if os.path.exists(path):
        raise MacroAlreadyExists()

    with open(path, "w") as f:
        f.write(json.dumps(macro))


def _deleteMacro(id: str):
    if id in _macroCache:
        _macroCache.pop(id)
    path = _getMacroPath(id)
    if os.path.exists(path):
        os.remove(path)
        return
    raise MacroDoesNotExist()

def _overwriteMacro(id:str, newMacro:dict):
    _deleteMacro(id)
    return _saveMacro(newMacro, id=id)

def _getMacro(id:str):
    if id in _macroCache:
        return _macroCache[id]

    path = _getMacroPath(id)
    if not os.path.exists(path):
        raise MacroDoesNotExist()

    with open(path, "r") as f:
        j = json.loads(f.read())

    j['id'] = id
    _macroCache[id] = j
    return j

def _getMacros():
    dir = os.listdir(const.macroFolder)
    macros = []
    for p in dir:
        macro = _getMacro(p.strip(".json"))
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

def _updateMacroName(id, name):
    macro = _getMacro(id)
    if macro['name'] == name:
        return
    macro['name'] = name
    _overwriteMacro(id, macro)


def _addCodeToMacro(id, code):
    global _rfMacroCodeLastAdded
    _rfMacroCodeLastAdded = time()

    macro = _getMacro(id)
    if 'code' not in macro or macro['code'] != code:
        macro['code'] = code
        _overwriteMacro(id, macro)

def _deleteMacroCode(id):
    macro = _getMacro(id)
    if 'code' in macro:
        macro.pop('code')
        _overwriteMacro(id, macro)

def _getMacroWithCode(code) -> Union[dict, None]:
    global _rfMacroCodeLastAdded
    if _rfMacroCodeLastAdded != None and time() -_rfMacroCodeLastAdded < const.rfMacroAddDebounceTime:
        return None

    macros = _getMacros()
    for macro in macros:
        if 'code' not in macro:
            continue
        macCode = macro['code']
        if code['code'] != macCode['code']:
            continue
        if code['protocol'] != macCode['protocol']:
            continue
        if abs(macCode['pulseLength'] - code['pulseLength']) > const.pulseLenthTolerance:
            continue
        return macro
    return None

