import os

from queue import Empty
from multiprocessing import Process, Queue
from typing import Union

import smart_home_server.constants as const
from smart_home_server import InterruptTriggered
from smart_home_server.handlers.presser.helpers import _changeChannel, _initRfDevice, _destroyRfDevice, _writeChannelValue, _removeChannel, _loadRemotes, \
                                                       _addRemote, _removeRemote, _remoteLock, remotes, RemoteDoesNotExist, _getRemoteById

_pressQueue:Union[None, Queue] = None
_presserThread:Union[None, Process] = None


def _presserLoop():
    global _pressQueue
    if _pressQueue is None:
        return
    _initRfDevice()
    _loadRemotes()

    # presser needs to have maximum priority
    if const.isRpi():
        pid = os.getpid()
        os.system("sudo renice -n -19 -p " + str(pid))

    while True:
        try:
            try:
                op = _pressQueue.get(block=True, timeout = const.threadPollingPeriod)
            except Empty:
                continue

            # None is stop singal
            if op is None:
                break

            for _ in range(const.pressRepeats+1):
                #_changeChannel(press['remote'], press['channel'], press['value'])
                op()
                #sleep(const.pressSpacing)

        except InterruptTriggered:
            break

        except Exception as e:
            print(f"Presser Exception: \n{repr(e)}", flush=True)
            continue

    _destroyRfDevice()


# API - start
def presserAppend(press):
    global _pressQueue
    if _pressQueue is None:
        return

    with _remoteLock:
        _changeChannel(press['id'], press['channel'], press['value'])

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

def writeChannelValue(id:str, channel: int, value: bool):
    with _remoteLock:
        return _writeChannelValue(id, channel, value)

def deleteChannel(id:str, channel: int):
    with _remoteLock:
        _removeChannel(id, channel)

def getRemoteById(id:str, throw=True):
    with _remoteLock:
        return _getRemoteById(id, throw=throw)
# API - end


def stopPresser():
    global _pressQueue
    if _pressQueue is None:
        return
    _pressQueue.put(None)

def joinPresser():
    global _pressQueue
    global _presserThread
    if _presserThread is not None and _presserThread.is_alive():
        if _pressQueue is not None:
            _pressQueue.put(None)
        _presserThread.join()

def startPresser():
    global _pressQueue
    global _presserThread

    stopPresser()
    joinPresser()
    _pressQueue = Queue()
    _presserThread = Process(target=_presserLoop)
    _presserThread.start()

    print("presser started")
