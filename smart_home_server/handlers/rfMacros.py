from threading import Thread
from typing import Union

from time import time, sleep

from smart_home_server.handlers.macros import getMacroWithCode
from smart_home_server.handlers.presser import readRemoteCode
from smart_home_server.handlers import runMacro

import smart_home_server.constants as const


_rfMacLoopCondition = False
_rfMacThread:Union[None, Thread] = None


_rfMacLastRan = None

def _rfMacLoop():
    global _rfMacLoopCondition
    global _rfMacLastRan

    while _rfMacLoopCondition:
        code = readRemoteCode(sleepTimer=0.1, timeout = const.threadPollingPeriod)
        if code is None:
            continue
        macro = getMacroWithCode(code)
        if macro is None or 'id' not in macro:
            continue
        now = time()
        if _rfMacLastRan is None or now - _rfMacLastRan > const.rfMacroDebounceTime:
            runMacro(macro['id'])
            _rfMacLastRan = now

def stopMac():
    global _rfMacLoopCondition
    _rfMacLoopCondition = False

def joinMac():
    global _rfMacThread
    if _rfMacThread is not None:
        if _rfMacThread.is_alive():
            _rfMacThread.join()
        _rfMacThread = None

def startMac():
    global _rfMacThread
    global _rfMacLoopCondition

    stopMac()
    joinMac()
    _rfMacLoopCondition = True
    _rfMacThread = Thread(target=_rfMacLoop, name="rfMac")
    _rfMacThread.start()

    print("rfMacros started")
