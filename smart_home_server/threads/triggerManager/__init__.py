from queue import Queue, Empty
from threading import Thread

from smart_home_server.helpers import clearQueue, waitUntil
from smart_home_server.threads.triggerManager.handlers import _addTrigger, _removeTrigger, _updateTriggerName, _enableDisableTrigger, _loadTriggers, _getTrigger, _getTriggers
import smart_home_server.constants as const

_triggerManagerEditQueue      = Queue()
_triggerManagerLoopCondition = False
_triggerManagerThread = None


def addTrigger(triggerJob:dict):
    global _triggerManagerEditQueue
    _triggerManagerEditQueue.put(lambda :_addTrigger(triggerJob))

def removeTrigger(id: str):
    global _triggerManagerEditQueue
    _triggerManagerEditQueue.put(lambda :_removeTrigger(id))

def enableDisableTrigger(id: str, enable=True):
    global _triggerManagerEditQueue
    _triggerManagerEditQueue.put(lambda :_enableDisableTrigger(id, enable=enable))

def loadTriggers():
    global _triggerManagerEditQueue
    _triggerManagerEditQueue.put(lambda :_loadTriggers())

def updateTriggerName(id: str, name: str):
    global _triggerManagerEditQueue
    _triggerManagerEditQueue.put(lambda :_updateTriggerName(id, name))

def getTrigger(id:str):
    triggerOut = []
    condition = [False]
    _triggerManagerEditQueue.put(lambda :_getTrigger(id, triggerOut, condition))
    waitUntil(lambda: condition[0])
    return triggerOut[0]

def getTriggers():
    triggerOut = []
    condition = [False]
    _triggerManagerEditQueue.put(lambda :_getTriggers(triggerOut, condition))
    waitUntil(lambda: condition[0])
    return triggerOut

def _triggerManagerLoop():
    global _triggerManagerLoopCondition
    global _triggerManagerEditQueue

    while _triggerManagerLoopCondition:
        try:
            while _triggerManagerEditQueue.qsize() != 0:
                try:
                    edit = _triggerManagerEditQueue.get(block=True)
                except Empty:
                    break
                edit()
            try:
                edit = _triggerManagerEditQueue.get(block=True, timeout=const.threadPollingPeriod)
            except Empty:
                continue
            edit()
        except Exception as e:
            print(f"Trigger Manager Exception: \n{repr(e)}", flush=True)
            continue


def stopTriggerManager():
    global _triggerManagerLoopCondition
    global _triggerManagerThread
    _triggerManagerLoopCondition = False

def joinTriggerManager():
    global _triggerManagerLoopCondition
    global _triggerManagerThread

    if _triggerManagerThread is not None and _triggerManagerThread.is_alive():
        _triggerManagerThread.join()
    _triggerManagerLoopCondition = False

def startTriggerManager():
    global _triggerManagerLoopCondition
    global _triggerManagerEditQueue
    global _triggerManagerThread
    if _triggerManagerLoopCondition:
        raise Exception("Trigger Manager Already Running")

    joinTriggerManager()

    clearQueue(_triggerManagerEditQueue)
    loadTriggers()
    _triggerManagerLoopCondition = True
    _triggerManagerThread = Thread(target=_triggerManagerLoop)
    _triggerManagerThread.start()
    print("Trigger Manager Started")
