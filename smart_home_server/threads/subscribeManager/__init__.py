from queue import Queue
from threading import Thread

from smart_home_server.data_sources import dataSourceValues, getSourceDict
from smart_home_server.threads.subscriber.helpers import _processSubs, _processUnsubs, _publishUpdates, Subscriber

_subThread = None
_subscribers = []
_toSend = {}
_newSubQueue = Queue()
_subLoopCondition = False

# name: time where name is source name
_lastUpdates = {}


def _subLoop():
    global _subscribers
    global _lastUpdates
    global _toSend
    global _subLoopCondition

    while _subLoopCondition:
        # blocks for a max of const.threadPollingPeriod
        _processSubs(_newSubQueue, _subscribers, _lastUpdates)
        _processUnsubs(_subscribers, _lastUpdates)
        _publishUpdates(_subscribers, _lastUpdates, _toSend)

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
    global _newSubQueue
    global _subThread
    if _subLoopCondition:
        raise Exception("Sub Loop Already Running")

    joinSubscribeManager()
    _newSubQueue = Queue()

    _subLoopCondition = True
    _subThread = Thread(target=_subLoop)
    _subThread.start()
    print("sub loop started")


def subscribe(values, cb, cbUnsub, cbError):
    global _newSubQueue
    values = {value for value in values if value in dataSourceValues}
    sourcesDict = getSourceDict(values)
    _newSubQueue.put(Subscriber(sourcesDict, values, cb, cbUnsub, cbError))


