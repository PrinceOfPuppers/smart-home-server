from time import sleep
import os

from queue import Empty
from multiprocessing import Process, Queue

import smart_home_server.constants as const
from smart_home_server import InterruptTriggered
from smart_home_server.handlers.presser.helpers import _changeChannel, _initRfDevice, _destroyRfDevice

from typing import Union

_pressQueue:Union[None, Queue] = None
_presserThread:Union[None, Process] = None

def _presserLoop():
    global _pressQueue
    if _pressQueue is None:
        return
    _initRfDevice()

    # presser needs to have maximum priority
    if const.isRpi():
        pid = os.getpid()
        os.system("sudo renice -n -19 -p " + str(pid))

    while True:
        try:
            try:
                press = _pressQueue.get(block=True, timeout = const.threadPollingPeriod)
            except Empty:
                continue

            # None is stop singal
            if press is None:
                break

            for _ in range(const.pressRepeats+1):
                _changeChannel(press['remote'], press['channel'], press['value'])
                #sleep(const.pressSpacing)

        except InterruptTriggered:
            break

        except Exception as e:
            print(f"Presser Exception: \n{repr(e)}", flush=True)
            continue

    _destroyRfDevice()

def presserAppend(press):
    global _pressQueue
    if _pressQueue is None:
        return
    _pressQueue.put(press)

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
