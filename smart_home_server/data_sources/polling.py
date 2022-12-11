import smart_home_server.constants as const
from datetime import datetime, timedelta
from time import sleep
from queue import Queue, Empty
from threading import Thread
from typing import Callable
from dataclasses import dataclass

from smart_home_server.data_sources import getSources, dataSourceValues, dataSourceDict, getSourceDict

def dataFromDataPath(x, dataPath):
    y = x
    for p in dataPath:
        y = y[p]
    return y

def updateToSend(source, toSend):
    func = source['local']
    res = func()
    if res is None:
        return
    for key,value in source['values'].items():
        if value['enabled']:
            try:
                data = dataFromDataPath(res , value['dataPath'])
            except KeyError:
                continue
            toSend[key] = data



# cb will be passed a dict like this: {"temp": 123, "wttrFeelsLike": 234} for each value in values
# note additional argumens may be passed
# funciton is blocking, will run until cbLoopCondition returns false
def polledUpdate(values, cb, cbLoopCondition, cbError, stopOnError = False):
    sources = getSources([value for value in values if value in dataSourceValues])

    # remove sources which have no values enabled
    for i in reversed(range(len(sources))):
        source = sources[i]
        anyEnabled = False
        for key in source['values']:
            val = source['values'][key]
            if val['enabled']:
                anyEnabled=True
                break
        if not anyEnabled:
            sources.pop(i)

    toSend = {}

    for source in sources:
        while True:
            try:
                updateToSend(source, toSend)
                break
            except Exception:
                sleep(0.1)


    cb(toSend)
    lastUpdate = datetime.now()

    while cbLoopCondition():
        sleep(const.threadPollingPeriod)
        try:
            now = datetime.now()
            updateOccured = False
            for source in sources:
                period = source['pollingPeriod']
                if now < lastUpdate+timedelta(seconds=period):
                    continue

                updateOccured = True
                lastUpdate = datetime.now()
                updateToSend(source, toSend)

            if updateOccured:
                cb(toSend)


        except Exception as e:
            cbError(e)
            if stopOnError:
                break

@dataclass
class Subscriber:
    # name: source where source is formatted as per dataSources
    sourcesDict: dict
    values: set
    cb: Callable
    cbUnsub: Callable
    cbError: Callable

_toSend = {}
_subscribers = []
_newSubQueue = Queue()
_subLoopCondition = False
_subLoopThread = None

# name: time where name is source name
_lastUpdates = {}

def filterAndCall(toSend:dict, values:set, f:Callable):
    s = {}
    for key in toSend:
        if key in values:
            s[key] = toSend[key]
    f(s)
    


def _processSub(sub, subscribers, lastUpdates):
    try:
        for name in sub.sourcesDict:
            # set last updated to a time long in the past so it will always trigger an update
            lastUpdates[name] = datetime.now() - timedelta(1000)
        subscribers.append(sub)
    except Empty:
        return

def _processSubs(subQueue:Queue, subscribers, lastUpdates):
    # blocking for a small amount of time
    try:
        sub:Subscriber = subQueue.get(block=True, timeout=const.threadPollingPeriod)
        _processSub(sub, subscribers, lastUpdates)
    except Empty:
        pass

    # process all if multiple where sent
    while True:
        try:
            sub:Subscriber = subQueue.get(block=False)
            _processSub(sub, subscribers, lastUpdates)
        except Empty:
            return

def _processUnsubs(subscribers, lastUpdates):
    for i in reversed(range(len(subscribers))):
        sub = subscribers[i]
        if not sub.cbUnsub():
            continue
        # do unsub
        subscribers.pop(i)
        # clear sources which have no other subscribers
        for name in sub.sourcesDict:
            if name not in lastUpdates:
                continue
            nameFound = False
            for otherSub in _subscribers:
                if name in otherSub.sourcesDict:
                    nameFound = True
                    break

            # other subscriber is subscribed to name
            if nameFound:
                break
            lastUpdates.pop(name)

def _publishUpdates(subscribers, lastUpdates, toSend):
    now = datetime.now()
    # update data if applicable
    for name in dataSourceDict:
        if name not in lastUpdates:
            continue
        source = dataSourceDict['name']
        period = source['pollingPeriod']
        if now < lastUpdates['name']+timedelta(seconds=period):
            # no update
            continue

        # do update
        lastUpdates[name] = now
        updateToSend(source, toSend)

    # publish updates
    for sub in subscribers:
        for name in sub.sourcesDict:
            if name in lastUpdates and lastUpdates[name]==now:
                filterAndCall(toSend, sub.values, sub.cb)
                break

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

def stopSubLoop():
    global _subLoopCondition
    global _subLoopThread
    _subLoopCondition = False

def joinSubLoop():
    global _subLoopCondition
    global _subLoopThread

    if _subLoopThread is not None and _subLoopThread.is_alive():
        _subLoopCondition = False
        _subLoopThread.join()
    else:
        _subLoopCondition = False

def startSubLoop():
    global _subLoopCondition
    global _newSubQueue
    global _subLoopThread
    if _subLoopCondition:
        raise Exception("Sub Loop Already Running")

    joinSubLoop()
    _newSubQueue = Queue()

    _subLoopCondition = True
    _subLoopThread = Thread(target=_subLoop)
    _subLoopThread.start()
    print("sub loop started")


def subscribe(values, cb, cbUnsub, cbError):
    global _newSubQueue
    values = {value for value in values if value in dataSourceValues}
    sourcesDict = getSourceDict(values)
    _newSubQueue.put(Subscriber(sourcesDict, values, cb, cbUnsub, cbError))


