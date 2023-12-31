import os
import json
from dataclasses import dataclass
from typing import Union
import string
import socket

from smart_home_server.errors import currentErrors
from smart_home_server.hardware_interfaces.lcd import writeLCD
from smart_home_server.hardware_interfaces.tcp import tcpSendPacket
import smart_home_server.constants as const
from smart_home_server.handlers.subscribeManager import subscribe

class LcdDoesNotExist(Exception):
    pass

class LcdAlreadyExists(Exception):
    pass

class LcdStopSig(Exception):
    pass


class IgnoreMissingDict(dict):
    def __missing__(self, key):
        return '{' + key + '}'

spaceFormat = "space"
noSpace = IgnoreMissingDict({spaceFormat:""})
oneSpace = IgnoreMissingDict({spaceFormat:" "})
def fillSpacesAndClamp(lines):
    res = []
    for i in range(min(len(lines), const.maxLcdLines)):
        line = lines[i]
        size = len(line.format_map(noSpace))
        numSpaces = len(line.format_map(oneSpace)) - size
        spaceSize = 0 if numSpaces < 1 else (const.lcdWidth - size)//numSpaces
        line = line.format_map(IgnoreMissingDict({spaceFormat:" "*spaceSize}))

        # clamp length
        line = line if len(line) <= const.lcdWidth else line[0:const.lcdWidth]
        res.append(line)

    return res

# writeCb takes in lines list
def _printfLCD(writeCb, fmt, replacements):
    try:
        text = fmt.format_map(IgnoreMissingDict(replacements))
        lines = text.split('\n')
        lines = fillSpacesAndClamp(lines)
    except Exception as e:
        print(f"LCD Format Error: \n{e}")
        currentErrors['Conseq_LCD_Write_Err'] += 1
        return

    try:
        ok = writeCb(lines)
    except Exception as e:
        print(f"LCD Write Error: \n{e}")
        currentErrors['Conseq_LCD_Write_Err'] += 1
        return

    if not ok:
        print("LCD Stop Sig Triggered")
        raise LcdStopSig
    currentErrors['Conseq_LCD_Write_Err'] = 0


@dataclass
class ActiveLcd:
    c:Union[socket.socket, None]
    num:int
    prevSent:str
    seq:int = 0

# sequence numbers for each lcd
_activeLcds = {}

_lcdCache = {}

def writeLcdRemote(num, c, lines):
    s = "\n".join(lines)
    if num in _activeLcds:
        if s == _activeLcds[num].prevSent:
            return True
        _activeLcds[num].prevSent = s
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

def _getLcds():
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

        lcds.append(lcd)

    return lcds


def _stopLcd(num, c: Union[socket.socket,None] = None):
    global _activeLcds
    if num in _activeLcds:
        print("Stopping LCD:", num)
        _activeLcds[num].seq += 1
        x = _activeLcds[num].c
        if x is not None:
            x.close()
    if c is not None:
        c.close()

def _stopAllLcds():
    for num in _activeLcds:
        _stopLcd(num)

def _subscribeErrCB(num, c, e:Exception):
    if isinstance(e, LcdStopSig):
        print("LCD Stop Sig Caught")
        _stopLcd(num, c)
    else:
        print(f"LCD Exception: \n{repr(e)}", flush=True)


def _notifyNotHookedup(num, c):
    print(f"Notifying LCD: {num} of no hookup")
    defaultLines = ["Open Dashboard to", "Set LCD Format"]
    if num == 0:
        writeLCD(defaultLines)
        return True

    return writeLcdRemote(num ,c, defaultLines)


def _startLcd(num, c:Union[socket.socket,None] = None):
    global _activeLcds
    print(f"Starting LCD: {num}")

    # shutdown previous running lcd
    _stopLcd(num)

    # if remote lcd, require port and ip
    if num != 0:
        assert c != None

    try:
        lcd = _getLcd(num)
    except LcdDoesNotExist:
        _notifyNotHookedup(num, c)
        return

    fmt = lcd['fmt']

    if num in _activeLcds:
        _activeLcds[num].c = c
        _activeLcds[num].prevSent = ""
    else:
        _activeLcds[num] = ActiveLcd(c, num, "", 0)

    current = _activeLcds[num].seq

    args = [tup[1] for tup in string.Formatter().parse(fmt) if tup[1] is not None]

    if num == 0: # if lcd is integrated one
        writeCb = lambda lines: writeLCD(lines)

    else: # if lcd is remote
        writeCb = lambda lines: writeLcdRemote(num, c, lines)

    subscribe(\
         args,
         lambda values:_printfLCD(writeCb, fmt, values),
         lambda: current != _activeLcds[num].seq,
         lambda e: _subscribeErrCB(num, c, e) # process errs and printfLCD WriteCB returning false
     )

def _restartLcd(num):
    global _activeLcds

    if num in _activeLcds:
        _startLcd(num, _activeLcds[num].c)


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

