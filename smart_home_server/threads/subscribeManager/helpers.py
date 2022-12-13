import smart_home_server.constants as const
from datetime import datetime, timedelta
from queue import Queue, Empty
from typing import Callable
from dataclasses import dataclass
from math import ceil

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

@dataclass
class GetOnce:
    sourcesDict: dict
    values: set
    cb: Callable
    cbError: Callable

def _filterAndCall(toSend:dict, values:set, f:Callable):
    s = {}
    for key in toSend:
        if key in values:
            s[key] = toSend[key]
    f(s)
    

def _withinMinUpdateTime(now, lastUpdate, pollingPeriod):
    return now - lastUpdate < timedelta(0, ceil(pollingPeriod/2))


def _processSub(now:datetime, sub, subscribers, lastUpdates):
    print(f"adding sub: {sub.values}")
    try:
        for name in sub.sourcesDict:
            lastUpdates[name] = now - timedelta(1000)
        subscribers.append(sub)
    except Empty:
        return

def _processGetOnce(now:datetime, once:GetOnce, lastUpdates, toSend):
    extraData = {}
    for name,source in once.sourcesDict.items():
        # check if source is already being subscribed to
        if name in lastUpdates:
            # check if data is still usable
            if _withinMinUpdateTime(now, lastUpdates[name], source['pollingPeriod']):
                continue
            _updateToSend(source, toSend)
            lastUpdates[name] = now

        # no subscribers fire and forget
        else:
            _updateToSend(once.sourcesDict[name], extraData)

    # merge data togeather
    extraData.update(toSend)
    try:
        _filterAndCall(extraData, once.values, once.cb)
    except Exception as e:
        once.cbError(e)

def _processUnsubs(subscribers, lastUpdates):
    for i in reversed(range(len(subscribers))):
        sub:Subscriber = subscribers[i]
        if not sub.cbUnsub():
            continue

        # do unsub
        print("unsubbing: ", sub.values)
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

def _publishUpdates(now: datetime, subscribers, lastUpdates, toSend):
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

