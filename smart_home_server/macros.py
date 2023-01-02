from uuid import uuid4
import os
import json
from time import sleep
from threading import Thread
import smart_home_server.constants as const
from smart_home_server.api import runJob
from threading import Lock

_macroLock = Lock()

class MacroDoesNotExist(Exception):
    pass

class MacroAlreadyExists(Exception):
    pass

class SequenceItemDoesNotExist(Exception):
    pass


def _getMacroPath(id:str):
    return f'{const.macroFolder}/{id}'

def saveMacro(macro:dict, id=None, lock=True):
    global _macroLock
    if lock:
        _macroLock.acquire()
    try:
        if id == None:
            id = str(uuid4())

        path = _getMacroPath(id)
        if os.path.exists(path):
            raise MacroAlreadyExists()

        with open(path, "w") as f:
            f.write(json.dumps(macro))
    finally:
        if lock:
            _macroLock.release()


def deleteMacro(id: str, lock = True):
    global _macroLock
    if lock:
        _macroLock.acquire()
    try:
        path = _getMacroPath(id)
        if os.path.exists(path):
            os.remove(path)
            return
        raise MacroDoesNotExist()
    finally:
        if lock:
            _macroLock.release()

def overwriteMacro(id:str, newMacro:dict, lock=True):
    global _macroLock
    if lock:
        _macroLock.acquire()
    try:
        deleteMacro(id, lock=False)
        return saveMacro(newMacro, id=id, lock=False)
    finally:
        if lock:
            _macroLock.release()

def getMacro(id:str, lock = True):
    global _macroLock
    if lock:
        _macroLock.acquire()
    try:
        path = _getMacroPath(id)
        if not os.path.exists(path):
            raise MacroDoesNotExist()

        with open(path, "r") as f:
            j = json.loads(f.read())

        j['id'] = id
        return j
    finally:
        if lock:
            _macroLock.release()

def getMacros():
    global _macroLock
    _macroLock.acquire()
    try:
        dir = os.listdir(const.macroFolder)
        macros = []
        for id in dir:
            macro = getMacro(id, lock = False)
            if macro is None:
                continue
            macros.append(macro)
        return macros
    finally:
        _macroLock.release()

macro = {
    "name": "Asdf",
    "id": "Asdf",
    "sequence": [
        {'id': "asdf", 'type': "delay", "data":{"minutes":5,"seconds": 3}},
        {'id': "asdf", 'type': "job", "data":{...}},
    ],
}

def addMacroSequenceItem(id, sequenceItem, index = -1):
    '''adds id to sequence item'''
    global _macroLock
    _macroLock.acquire()
    try:
        macro = getMacro(id, lock=False)
        sequenceItemId = str(uuid4())
        sequenceItem['id'] = sequenceItemId
        if index == -1:
            macro['sequence'].append(sequenceItem)
        else:
            index = min(max(index,0), len(macro['sequence']))
            macro['sequence'].insert(index, sequenceItem)

        overwriteMacro(macro['id'], macro, lock=False)
    finally:
        _macroLock.release()

def deleteMacroSequenceItem(macroId, sequenceItemId):
    global _macroLock
    _macroLock.acquire()
    try:
        macro = getMacro(macroId, lock=False)
        for i,item in enumerate(macro['sequence']):
            if item['id'] == sequenceItemId:
                macro['sequence'].pop(i)
                overwriteMacro(macro['id'], macro, lock=False)
                return
        raise SequenceItemDoesNotExist()
    finally:
        _macroLock.release()

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

def runMacro(id):
    global _macroLock
    macro = getMacro(id)
    name = macro['name']
    sequence = macro['sequence']
    print(f"Running Macro: {name}")
    _runMacroSequence(sequence)

