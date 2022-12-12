import smart_home_server.constants as const
from datetime import datetime, timedelta
from queue import Queue, Empty
from typing import Callable
from dataclasses import dataclass

from smart_home_server.data_sources import dataSourceDict

def _dataFromDataPath(x, dataPath):
    y = x
    for p in dataPath:
        y = y[p]
    return y

def _updateToSend(source, toSend):
    func = source['local']
    res = func()
    if res is None:
        return
    for key,value in source['values'].items():
        # we do not check if enabled, its only used for frontend filtering
        #if value['enabled']:
        try:
            data = _dataFromDataPath(res , value['dataPath'])
        except KeyError:
            continue
        toSend[key] = data


@dataclass
class Subscriber:
    # name: source where source is formatted as per dataSources
    sourcesDict: dict
    values: set
    cb: Callable
    cbUnsub: Callable
    cbError: Callable

def _filterAndCall(toSend:dict, values:set, f:Callable):
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
        sub:Subscriber = subscribers[i]
        if not sub.cbUnsub():
            continue

        # do unsub
        subscribers.pop(i)
        # clear sources which have no other subscribers
        for name in sub.sourcesDict:
            if name not in lastUpdates:
                continue
            nameFound = False
            for otherSub in subscribers:
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
        source = dataSourceDict[name]
        period = source['pollingPeriod']
        if now < lastUpdates[name]+timedelta(seconds=period):
            # no update
            continue

        # do update
        try:
            _updateToSend(source, toSend)
            lastUpdates[name] = now
        except Exception as e:
            for sub in subscribers:
                if name in sub.sourcesDict:
                    sub.cbError(e)

    # publish updates
    for sub in subscribers:
        for name in sub.sourcesDict:
            if name in lastUpdates and lastUpdates[name]==now:
                _filterAndCall(toSend, sub.values, sub.cb)
                break

