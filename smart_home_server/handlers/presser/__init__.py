import os

from queue import Empty
from multiprocessing import Process, Queue
from typing import Union

import smart_home_server.constants as const
from smart_home_server import InterruptTriggered
from smart_home_server.handlers.presser.helpers import _changeChannel, _initRfDevices, _destroyRfDevices, _removeChannel, RemoteDoesNotExist, ChannelDoesNotExist, \
                                                       _addRemote, _removeRemote, _remoteLock, _getRemoteById, _getRemotes, _getCode, _addChannel

_pressQueue:Union[None, Queue] = None
_presserThread:Union[None, Process] = None


def _presserLoop():
    global _pressQueue
    if _pressQueue is None:
        return

    # presser needs to have maximum priority
    if const.isRpi():
        pid = os.getpid()
        os.system("sudo renice -n -19 -p " + str(pid))

    while True:
        try:
            try:
                p = _pressQueue.get(block=True, timeout = const.threadPollingPeriod)
            except Empty:
                continue

            # None is stop singal
            if p is None:
                break

            _changeChannel(p['remote'], p['channel'], p['value'])

        except InterruptTriggered:
            break

        except Exception as e:
            print(f"Presser Exception: \n{repr(e)}", flush=True)
            continue


# API - start
def presserAppend(press):
    global _pressQueue
    if _pressQueue is None:
        return

    with _remoteLock:
        remote = _getRemoteById(press['id'], throw=True)

    p = {"remote": remote, "channel": press['channel'], "value": press['value']}
    _pressQueue.put(p)

def newRemote(name:str):
    global _pressQueue
    if _pressQueue is None:
        return

    remote = {"name": name, "channels": []}
    with _remoteLock:
        _addRemote(remote)

def deleteRemote(id:str):
    global _pressQueue
    if _pressQueue is None:
        return

    with _remoteLock:
        _removeRemote(id)

def readRemoteCode(timeout = 10, repeats = 3, sleepTimer = 0.01) -> Union[dict, None]:
    return _getCode(timeout, repeats, sleepTimer)

def addChannel(id:str, channel: int, onCode:dict, offCode:dict):
    with _remoteLock:
        return _addChannel(id, channel, onCode, offCode)

def deleteChannel(id:str, channel: int):
    with _remoteLock:
        _removeChannel(id, channel)

def getRemoteById(id:str, throw=True):
    with _remoteLock:
        return _getRemoteById(id, throw=throw)

def getRemotes():
    return _getRemotes()

# API - end


def stopPresser():
    global _pressQueue
    if _pressQueue is None:
        return
    _pressQueue.put(None)
    _pressQueue.close()

    _destroyRfDevices()

def joinPresser():
    global _pressQueue
    global _presserThread

    if _presserThread is not None and _presserThread.is_alive():
        _presserThread.join()

    if _pressQueue is not None:
        _pressQueue.join_thread()

def startPresser():
    global _pressQueue
    global _presserThread

    stopPresser()
    joinPresser()
    _initRfDevices()
    _pressQueue = Queue()
    _presserThread = Process(target=_presserLoop)
    _presserThread.start()

    print("presser started")
