from threading import Lock
from smart_home_server.threads.triggerManager.helpers import _addTrigger, _removeTrigger, _updateTriggerName, _enableDisableTrigger, _loadTriggers, _getTrigger, _getTriggers

_triggerLock = Lock()


def addTrigger(triggerJob:dict):
    with _triggerLock:
        _addTrigger(triggerJob)

def removeTrigger(id: str):
    with _triggerLock:
        _removeTrigger(id)

def enableDisableTrigger(id: str, enable=True):
    with _triggerLock:
        _enableDisableTrigger(id, enable=enable)

def loadTriggers():
    with _triggerLock:
        _loadTriggers()

def updateTriggerName(id: str, name: str):
    with _triggerLock:
        _updateTriggerName(id, name)

def getTrigger(id:str):
    with _triggerLock:
        return _getTrigger(id)

def getTriggers():
    with _triggerLock:
        return _getTriggers()

