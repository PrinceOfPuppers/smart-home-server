import os
import json
from dataclasses import dataclass
from typing import Union
import string

from smart_home_server.errors import currentErrors 
from smart_home_server.hardware_interfaces.lcd import writeLCD
from smart_home_server.hardware_interfaces.udp import udpWriteAck
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
    for i in range(min(len(lines), const.lcdLines)):
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
def printfLCD(writeCb, fmt, replacements):
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
        raise LcdStopSig
    currentErrors['Conseq_LCD_Write_Err'] = 0
 


@dataclass
class ActiveLcd:
    ip:Union[str,None]
    port:Union[int, None]
    num:int
    seq:int = 0

# sequence numbers for each lcd
_activeLcds = {}

_lcdCache = {}

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


def _stopLcd(num):
    global _activeLcds
    if num in _activeLcds:
        _activeLcds[num].seq += 1

def _subscribeErrCB(num, e:Exception):
    if isinstance(e, LcdStopSig):
        _stopLcd(num)
    else:
        print(f"LCD Exception: \n{repr(e)}", flush=True)



def startLcd(num, ip = None, port = None):
    global _activeLcds

    # shutdown previous running lcd
    _stopLcd(num)

    lcd = _getLcd(num)
    fmt = lcd['fmt']

    # if remote lcd, require port and ip
    if num != 0:
        assert ip != None
        assert port != None

    if num in _activeLcds:
        _activeLcds[num].ip = ip
        _activeLcds[num].port = port
    else:
        _activeLcds[num] = ActiveLcd(ip, port, num, 0)

    current = _activeLcds[num].seq

    args = [tup[1] for tup in string.Formatter().parse(fmt) if tup[1] is not None]

    if num == 0:
        writeCb = lambda lines: writeLCD(lines)
    else:
        assert ip != None
        assert port != None
        writeCb = lambda lines: udpWriteAck(ip, port, lines)

    subscribe(\
         args, 
         lambda values:printfLCD(writeCb, fmt, values), 
         lambda: current != _activeLcds[num].seq, 
         lambda e: _subscribeErrCB(num, e) # process errs and printfLCD WriteCB returning false
     )

def restartLcd(num):
    global _activeLcds

    if num in _activeLcds:
        startLcd(num, _activeLcds[num].ip, _activeLcds[num].port)


def _saveLcd(num:int, lcd:dict):
    global _lcdCache
    lcd["num"] = num

    _lcdCache[num] = lcd

    path = _getLcdPath(num)
    if os.path.exists(path):
        raise LcdAlreadyExists()

    with open(path, "w") as f:
        f.write(json.dumps(lcd))

    restartLcd(num)

def _deleteLcd(num: int):
    if num in _lcdCache:
        _lcdCache.pop(num)
    path = _getLcdPath(num)
    if os.path.exists(path):
        os.remove(path)
        return
    raise LcdDoesNotExist()


def _overwriteLcd(num:int, newLcd:dict):
    _deleteLcd(num)
    return _saveLcd(num, newLcd)

