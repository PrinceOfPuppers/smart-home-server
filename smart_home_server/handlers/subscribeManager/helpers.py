import smart_home_server.constants as const
from datetime import datetime, timedelta
from queue import Queue, Empty
from typing import Callable
from dataclasses import dataclass
from math import ceil
import traceback

from smart_home_server.data_sources import dataSourceDict
from smart_home_server.errors import currentErrors

def _dataFromDataPath(x, dataPath):
    y = x
    for p in dataPath:
        y = y[p]
    return y

def _updateToSend(source, toSend):
    global currentErrors
    func = source['local']
    res = func()
    if res is None:
        # add error
        currentErrors['Subscribe_Manager_None'].add(source['name'])
        return

    # remove error if it exists
    currentErrors['Subscribe_Manager_None'].discard(source['name'])

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
    try:
        f(s)
    except Exception as e:
        print(f'SubLoop _filterAndCall Error: \n{e}')
        print(f"Trace:\n{traceback.format_exc()}")
    

def _processSub(now:datetime, sub, subscribers, lastUpdates):
    print(f"adding sub: {sub.values}")
    try:
        for name in sub.sourcesDict:
            lastUpdates[name] = now - timedelta(1000)
        subscribers.append(sub)
    except Empty:
        return

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
            print(f'SubLoop _updateToSend Error: \n{repr(e)}')
            print(f"Trace:\n{traceback.format_exc()}")
            for sub in subscribers:
                if name in sub.sourcesDict:
                    sub.cbError(e)

    # publish updates
    for sub in subscribers:
        for name in sub.sourcesDict:
            if name in lastUpdates and lastUpdates[name]==now:
                _filterAndCall(toSend, sub.values, sub.cb)
                break

