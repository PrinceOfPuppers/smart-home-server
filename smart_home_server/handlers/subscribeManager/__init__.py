from queue import Queue,Empty
from threading import Thread
from datetime import datetime

from smart_home_server.data_sources import dataSourceValues, getSourceDict
from smart_home_server.handlers.subscribeManager.helpers import _processUnsubs, _publishUpdates, Subscriber, _processSub
import smart_home_server.constants as const

_subThread = None
_subscribers = []
_toSend = {}
_subManagerJobQueue = Queue()
_subLoopCondition = False

# name: time where name is source name
_lastUpdates = {}

def _processSubs(now, subManagerJobQueue, subscribers, lastUpdates):
    # blocking for a small amount of time
    try:
        sub = subManagerJobQueue.get(block=True, timeout=const.threadPollingPeriod)
        if isinstance(sub, Subscriber):
            _processSub(now, sub, subscribers, lastUpdates)
    except Empty:
        pass

    # process all if multiple where sent
    while True:
        try:
            sub = _subManagerJobQueue.get(block=False)
            if isinstance(sub, Subscriber):
                _processSub(now, sub, subscribers, lastUpdates)
        except Empty:
            break

def _subLoop():
    global _subscribers
    global _lastUpdates
    global _toSend
    global _subLoopCondition
    global _subManagerJobQueue

    while _subLoopCondition:
            now = datetime.now()
            _processSubs(now, _subManagerJobQueue, _subscribers, _lastUpdates)
            _processUnsubs(_subscribers, _lastUpdates)
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
