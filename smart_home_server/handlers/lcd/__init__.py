import string
from typing import Union
from threading import Lock, Thread
from datetime import datetime

import smart_home_server.constants as const
from smart_home_server.handlers.lcd.helpers import startLcd
from smart_home_server.hardware_interfaces.udp import udpListener

lcdLock = Lock()
_lcdListenLoopCondition = False

def addLcd(ip, port, lcdNumStr):
    # must return expected polling period
    try: 
        lcdNum = int(lcdNumStr)
        startLcd(lcdNum, ip, port)
    except:
        return

def stopLcdListener():
    global _lcdListenerLoopCondition
    _lcdListenerLoopCondition = False

def joinLcdListener():
    global _lcdListenerLoopCondition
    global _lcdListenerThread

    if _lcdListenerThread is not None and _lcdListenerThread.is_alive():
        _lcdListenerLoopCondition = False
        _lcdListenerThread.join()
    else:
        _lcdListenerLoopCondition = False

def startLcdListener():
    global _lcdListenerLoopCondition
    global _lcdListenerThread
    if _lcdListenerLoopCondition:
        raise Exception("LcdListener Already Running")

    joinLcdListener()

    print(f"LcdListener Load Time: {datetime.now()}")
    _lcdListenerLoopCondition = True
    _lcdListenerThread = Thread(target=lambda: udpListener(const.lcdListenerPort, addLcd, lambda: _lcdListenLoopCondition))
    _lcdListenerThread.start()
    print("lcdListener started")

