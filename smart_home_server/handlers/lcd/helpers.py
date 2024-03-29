import os
from datetime import datetime
import json
from dataclasses import dataclass
from typing import Union
import string
import socket
from threading import Lock

from smart_home_server.errors import incConseqError, clearConseqError, addFlagError, clearFlagError
from smart_home_server.hardware_interfaces.lcd import writeLCD, setBacklight, toggleBacklight
from smart_home_server.hardware_interfaces.tcp import tcpSendPacket, disconnectSocket
import smart_home_server.constants as const
from smart_home_server.handlers.subscribeManager import subscribe
from smart_home_server.handlers.lcd.formatter import IgnoreMissingFormatter

class LcdDoesNotExist(Exception):
    pass

class LcdAlreadyExists(Exception):
    pass

class LcdStopSig(Exception):
    pass

spaceFormat = "space"
noSpace = {spaceFormat:""}
oneSpace = {spaceFormat:" "}

formatter = IgnoreMissingFormatter()
def fillSpacesAndClamp(lines):
    res = []
    for i in range(min(len(lines), const.maxLcdLines)):
        line = lines[i]
        size = len(formatter.format(line, **noSpace))
        numSpaces = len(formatter.format(line, **oneSpace)) - size
        spaceSize = 0 if numSpaces < 1 else (const.lcdWidth - size)//numSpaces
        line = formatter.format(line, **{spaceFormat:" "*spaceSize})

        # clamp length
        line = line if len(line) <= const.lcdWidth else line[0:const.lcdWidth]
        res.append(line)

    return res

# writeCb takes in lines list
def _printfLCD(writeCb, fmt, replacements):
    try:
        text = formatter.format(fmt, **replacements)
        lines = text.split('\n')
        lines = fillSpacesAndClamp(lines)
    except Exception as e:
        print(f"LCD Format Error: \n{e}")
        incConseqError("LCD Write Err")
        return

    try:
        ok = writeCb(lines)
    except Exception as e:
        print(f"LCD Write Error: \n{e}")
        incConseqError("LCD Write Err")
        return

    if not ok:
        print("LCD Stop Sig Triggered")
        raise LcdStopSig
    clearConseqError("LCD Write Err")


@dataclass
class ActiveLcd:
    c:Union[socket.socket, None]
    num:int
    prevSent:str
    seq:int = 0

# sequence numbers for each lcd
_activeLcds = {}
_activeLcdsLock = Lock()

_lcdCache = {}

def _lcdActive(num, lock=True):
    global _activeLcds
    if lock:
        _activeLcdsLock.acquire()
    try:

        if num in _activeLcds and _activeLcds[num].c is not None:
            return True
        return False

    finally:
        if lock:
            _activeLcdsLock.release()

def writeLcdRemote(num, c, lines, lock=True):
    global _activeLcds
    s = "\n".join(lines)
    if lock:
        _activeLcdsLock.acquire()
    try:
        if num in _activeLcds:
            if s == _activeLcds[num].prevSent:
                return True
            _activeLcds[num].prevSent = s
    finally:
        if lock:
            _activeLcdsLock.release()
    return tcpSendPacket(c, "\n".join(lines))

def _getLcdPath(num:int):
    return f'{const.lcdsFolder}/{num}.json'

def _getLcd(num:int):
    if num in _lcdCache:
        return _lcdCache[num]

    path = _getLcdPath(num)
    if not os.path.exists(path):
        raise LcdDoesNotExist()

    with open(path, "r") as f:
        j = json.loads(f.read())

    j['num'] = num
    _lcdCache[num] = j
    return j

def _getLcds(tagActive=False):
    dir = os.listdir(const.lcdsFolder)
    lcds = []

    for p in dir:
        s = p.strip(".json")

        try:
            num = int(s)
        except:
            os.remove(f'{const.lcdsFolder}/{p}')
            continue

        try:
            lcd = _getLcd(num)
        except:
            continue
        if tagActive:
            lcd["active"] = True if num == 0 else _lcdActive(num)
        lcds.append(lcd)

    return lcds



def _stopLcd(num, lock = True):
    global _activeLcds
    if lock:
        _activeLcdsLock.acquire()
    try:
        if num in _activeLcds:
            print("Stopping LCD:", num)
            _activeLcds[num].seq += 1
    finally:
        if lock:
            _activeLcdsLock.release()

def _disconnectLcd(num, c: Union[socket.socket,None] = None, lock = True):
    global _activeLcds

    if lock:
        _activeLcdsLock.acquire()
    try:
        if num in _activeLcds:
            if c is not None and _activeLcds[num].c != c:
                pass # we are dealing with an old connection, no longer in _activeLcds
            else:
                print("Disconneting LCD:", num)
                _activeLcds[num].seq += 1
                if _activeLcds[num].c is not None:
                    disconnectSocket(_activeLcds[num].c)
                _activeLcds[num].c = None

    finally:
        if lock:
            _activeLcdsLock.release()

    # redundant check of c, but harmless
    if c is not None:
        disconnectSocket(c)


def _disconnectAllLcds():
    global _activeLcds
    for num in list(_activeLcds.keys()):
        _disconnectLcd(num)

def _subscribeErrCB(num, c, e:Exception):
    if isinstance(e, LcdStopSig):
        print("LCD Stop Sig Caught")
        _disconnectLcd(num, c)
    else:
        print(f"LCD Exception: \n{repr(e)}", flush=True)
        return


def _notifyNotHookedup(num, c):
    print(f"Notifying LCD: {num} of no hookup")
    defaultLines = ["Open Dashboard to", f"Set LCD {num} Format"]
    if num == 0:
        writeLCD(defaultLines)
        return True

    return writeLcdRemote(num ,c, defaultLines, lock=False)


def _startLcd(num, c:Union[socket.socket,None] = None, disconnect = True, lock = True):
    global _activeLcds
    if lock:
        _activeLcdsLock.acquire()
    try:
        # shutdown previous running lcd
        if disconnect:
            _disconnectLcd(num, lock=False)
        else:
            _stopLcd(num, lock=False)

        print(f"Starting LCD: {num}")

        # if remote lcd, require port and ip
        if num != 0:
            assert c != None


        if num in _activeLcds:
            _activeLcds[num].c = c
            _activeLcds[num].prevSent = ""
        else:
            _activeLcds[num] = ActiveLcd(c, num, "", 0)

        try:
            lcd = _getLcd(num)
        except LcdDoesNotExist:
            _notifyNotHookedup(num, c)
            return

        fmt = lcd['fmt']
        firstMessage = fillSpacesAndClamp(fmt.split("\n"))

        current = _activeLcds[num].seq

        args = [tup[1] for tup in string.Formatter().parse(fmt) if tup[1] is not None]

        if num == 0: # if lcd is integrated one
            writeCb = lambda lines: writeLCD(lines)
            writeLCD(firstMessage)

        else: # if lcd is remote
            writeCb = lambda lines: writeLcdRemote(num, c, lines)
            writeLcdRemote(num, c, firstMessage, lock=False)

        subscribe(\
             args,
             lambda values:_printfLCD(writeCb, fmt, values),
             lambda: current != _activeLcds[num].seq,
             lambda e: _subscribeErrCB(num, c, e) # process errs and printfLCD WriteCB returning false
         )
    finally:
        if lock:
            _activeLcdsLock.release()


def _restartLcd(num):
    global _activeLcds

    with _activeLcdsLock:
        if num in _activeLcds:
            print(f"Restarting LCD: {num}")
            _startLcd(num, _activeLcds[num].c, disconnect=False, lock = False)


def _saveLcd(num:int, lcd:dict):
    global _lcdCache
    lcd["num"] = num
    if not "name" in lcd:
        lcd["name"] = const.lcdDefaultName
    if not "fmt" in lcd:
        lcd["fmt"] = ""

    _lcdCache[num] = lcd

    path = _getLcdPath(num)
    if os.path.exists(path):
        raise LcdAlreadyExists()

    with open(path, "w") as f:
        f.write(json.dumps(lcd))

    _restartLcd(num)

def _deleteLcd(num: int, restart = False):
    if num in _lcdCache:
        _lcdCache.pop(num)
    path = _getLcdPath(num)
    if os.path.exists(path):
        os.remove(path)
        if restart:
            _restartLcd(num)
        return
    if restart:
        _restartLcd(num)
    raise LcdDoesNotExist()


def _overwriteLcd(num:int, newLcd:dict):
    _deleteLcd(num)
    return _saveLcd(num, newLcd)

def _setBacklight(num:int, on:bool):
    if num==0:
        setBacklight(on)
        return
    with _activeLcdsLock:
        if num in _activeLcds:
            tcpSendPacket(_activeLcds[num].c, const.lcdCmdEscapeChar + "l" + ("1" if on else "0"))

def _toggleBacklight(num:int):
    if num==0:
        toggleBacklight()
        return
    with _activeLcdsLock:
        if num in _activeLcds:
            tcpSendPacket(_activeLcds[num].c, const.lcdCmdEscapeChar + "lt")

