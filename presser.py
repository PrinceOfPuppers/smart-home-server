from time import sleep
from queue import Queue
from threading import Thread

import constants as const

_pressQueue = Queue()
_pressLoop=True

def changeChannel(channel: int, value: bool):
    print(f'{channel=}', f'{value=}', flush=True)

def presserLoop():
    global _pressQueue
    global _pressLoop
    while _pressLoop:
        press = _pressQueue.get()
        for _ in range(const.pressRepeats+1):
            changeChannel(press['channel'], press['value'])
            sleep(const.pressSpacing)

def presserAppend(press):
    global _pressQueue
    _pressQueue.put(press)

def startPresser():
    global _pressQueue
    global _pressLoop
    _pressQueue.empty()
    _pressLoop = True
    Thread(target=presserLoop).start()

def stopPresser():
    global _pressLoop
    _pressLoop = False
