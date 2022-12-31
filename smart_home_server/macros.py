from uuid import uuid4
import os
import json
import smart_home_server.constants as const
from smart_home_server.api import runJob
from threading import Lock

_macroLock = Lock()

class MacroDoesNotExist(Exception):
    pass

class MacroAlreadyExists(Exception):
    pass

def _getMacroPath(id:str):
    return f'{const.macroFolder}/{id}'

def createMacro(name:str, jobs:dict, id=None, lock=True):
    global _macroLock
    try:
        if lock:
            _macroLock.acquire()
        if id == None:
            id = str(uuid4())

        path = _getMacroPath(id)
        if os.path.exists(path):
            raise MacroAlreadyExists()

        name = name.replace('\n', ' ').strip()
        with open(path, "w") as f:
            f.write(json.dumps({"name":name, "jobs":jobs}))
    finally:
        if lock:
            _macroLock.release()


def deleteMacro(id: str, lock = True):
    global _macroLock
    try:
        if lock:
            _macroLock.acquire()
        path = _getMacroPath(id)
        if os.path.exists(path):
            os.remove(path)
            return
        raise MacroDoesNotExist()
    finally:
        if lock:
            _macroLock.release()

def updateMacro(id:str, name:str=None, jobs:dict=None):
    global _macroLock
    _macroLock.acquire()
    try:
        macro = getMacro(id, lock=False)
        if macro is None:
            return MacroDoesNotExist()
        name = macro['name'] if name is None else name
        jobs = macro['jobs'] if jobs is None else jobs
        deleteMacro(id, lock=False)
        return createMacro(name, jobs, id=id, lock=False)
    finally:
        _macroLock.release()

def getMacro(id:str, lock = True):
    global _macroLock
    try:
        if lock:
            _macroLock.acquire()
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

def runMacro(id):
    _macroLock.acquire()
    try:
        macro = getMacro(id, lock=False)
        print(f"Running Macro: {macro['name']}")
        jobs = macro['jobs']
        for job in jobs:
            runJob(job)
    finally:
        _macroLock.release()
