from uuid import uuid4
import os
import json
import smart_home_server.constants as const

class MacroDoesNotExist(Exception):
    pass

class MacroAlreadyExists(Exception):
    pass

class SequenceItemDoesNotExist(Exception):
    pass


def _getMacroPath(id:str):
    return f'{const.macroFolder}/{id}.json'


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

