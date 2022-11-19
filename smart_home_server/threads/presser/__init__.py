from time import sleep
from queue import Queue, Empty
from threading import Thread

import smart_home_server.constants as const
from smart_home_server.helpers import clearQueue

_pressQueue = Queue()
_presserLoopCondition  = False
_presserThread = None

def _changeChannel(channel: int, value: bool):
    print(f'{channel=}', f'{value=}', flush=True)

def _presserLoop():
    global _pressQueue
    global _presserLoopCondition
    while _presserLoopCondition:
        try:
            press = _pressQueue.get(block=True, timeout = 1)
        except Empty:
            continue
        for _ in range(const.pressRepeats+1):
            _changeChannel(press['channel'], press['value'])
            sleep(const.pressSpacing)

def presserAppend(press):
    global _pressQueue
    _pressQueue.put(press)

def startPresser():
    global _pressQueue
    global _presserLoopCondition
    global _presserThread
    if _presserLoopCondition:
        raise Exception("Presser Already Running")

    clearQueue(_pressQueue)
    _presserThread = Thread(target=_presserLoop)
    _presserThread.start()
    print("presser started")

def stopPresser():
    global _presserLoopCondition
    _presserLoopCondition = False

def joinPresser():
    global _presserLoopCondition
    global _presserThread
    if _presserThread is not None and _presserThread.is_alive():
        _presserLoopCondition = False
        _presserThread.join()
    else:
        _presserLoopCondition = False
    print("presser joined")
