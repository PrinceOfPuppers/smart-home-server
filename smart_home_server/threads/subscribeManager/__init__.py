from queue import Queue,Empty
from threading import Thread
from datetime import datetime
from smart_home_server.helpers import waitUntil
from typing import Union
from functools import partial

from smart_home_server.data_sources import dataSourceValues, getSourceDict
from smart_home_server.threads.subscribeManager.helpers import _processGetOnce, _processUnsubs, _publishUpdates, Subscriber, GetOnce, _processSub
import smart_home_server.constants as const

_subThread = None
_subscribers = []
_toSend = {}
_subManagerJobQueue = Queue()
_subLoopCondition = False

# name: time where name is source name
_lastUpdates = {}

def _addJob(job, newSubs, newGetOnce):
    if job is not None:
        if isinstance(job, Subscriber):
            newSubs.append(job)
        else:
            newGetOnce.append(job)
def _addJobs(newSubs, newGetOnce):
    global _subManagerJobQueue
    # blocking for a small amount of time
    try:
        job = _subManagerJobQueue.get(block=True, timeout=const.threadPollingPeriod)
        _addJob(job, newSubs, newGetOnce)
    except Empty:
        pass

    # process all if multiple where sent
    while True:
        try:
            job = _subManagerJobQueue.get(block=False)
            _addJob(job, newSubs, newGetOnce)
        except Empty:
            break

def _subLoop():
    global _subscribers
    global _lastUpdates
    global _toSend
    global _subLoopCondition
    global _subManagerJobQueue

    while _subLoopCondition:
        newSubs=[]
        newGetOnce=[]
        _addJobs(newSubs, newGetOnce)

        now = datetime.now()

        for sub in newSubs:
            _processSub(now, sub, _subscribers, _lastUpdates)

        _processUnsubs(_subscribers, _lastUpdates)

        for once in newGetOnce:
            _processGetOnce(now, once, _lastUpdates, _toSend)

        _publishUpdates(now, _subscribers, _lastUpdates, _toSend)

def stopSubscribeManager():
    global _subLoopCondition
    global _subThread
    _subLoopCondition = False

def joinSubscribeManager():
    global _subLoopCondition
    global _subThread

    if _subThread is not None and _subThread.is_alive():
        _subLoopCondition = False
        _subThread.join()
    else:
        _subLoopCondition = False

def startSubscribeManager():
    global _subLoopCondition
    global _subManagerJobQueue
    global _subThread

    if _subLoopCondition:
        raise Exception("Sub Loop Already Running")

    joinSubscribeManager()

    _subLoopCondition = True
    _subThread = Thread(target=_subLoop)
    _subThread.start()
    print("sub loop started")


def subscribe(values, cb, cbUnsub, cbError):
    global _subManagerJobQueue
    values = {value for value in values if value in dataSourceValues}
    sourcesDict = getSourceDict(values)
    _subManagerJobQueue.put(Subscriber(sourcesDict, values, cb, cbUnsub, cbError))

def _GetOnce(dataOut, conditionOut, data):
    dataOut.append(data)
    conditionOut[0] = True

# terrible function to fix callback hell
def getOnce(values) -> Union[dict, Exception]:
    values = {value for value in values if value in dataSourceValues}
    dataOut = []
    conditionOut = [False]
    f = lambda data: _GetOnce(dataOut, conditionOut, data)
    sourcesDict = getSourceDict(values)
    _subManagerJobQueue.put(GetOnce(sourcesDict, values, f, f))
    waitUntil(lambda: conditionOut[0])
    return dataOut[0]

