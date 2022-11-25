import string
from datetime import datetime, timedelta
from collections import defaultdict
from time import sleep
from threading import Thread

import smart_home_server.constants as const
from smart_home_server.threads.lcd.helpers import getPeriodPairs, fillSpacesAndClamp
from smart_home_server.hardware_interfaces.lcd import writeLCD, toggleBacklight

_lcdThread = None
_lcdLoopCondition = False

# used to get current format for dashboard
_fmt = ""

class IgnoreMissingDict(dict):
    def __missing__(self, key):
        return '{' + key + '}'

def printfLCD(fmt, replacements):
    text = fmt.format_map(IgnoreMissingDict(replacements))
    lines = text.split('\n')
    lines = fillSpacesAndClamp(lines)
    text = '\n'.join(lines)

    writeLCD(text)

def _lcdLoop(fmt, args, replacements, periodPairs):
    global _lcdLoopCondition
    printfLCD(fmt, replacements)
    lastUpdate = datetime.now()

    while _lcdLoopCondition:
        try:
            now = datetime.now()

            for period, func in periodPairs:
                if now < lastUpdate+timedelta(seconds=period):
                    continue

                # update format string
                func(args,replacements)
                printfLCD(fmt, replacements)
                lastUpdate = datetime.now()

            sleep(1)
        except Exception as e:
            print(f"LCD Exception: \n{e}", flush=True)
            continue

def _startLCD(fmt):
    global _fmt
    _fmt = fmt
    args = {tup[1] for tup in string.Formatter().parse(fmt) if tup[1] is not None}

    if len(args) == 0:
        printfLCD(fmt, {}) # no updates, static text
        return

    replacements = {}

    periodPairs = getPeriodPairs(args, replacements)

    _lcdLoop(fmt, args, replacements, periodPairs)


def stopLCD():
    global _lcdLoopCondition

    if const.isRpi():
        # TODO: gpio resources
        pass

    _lcdLoopCondition = False

def joinLCD():
    global _lcdLoopCondition
    global _lcdThread
    if _lcdThread is not None and _lcdThread.is_alive():
        _lcdLoopCondition = False
        _lcdThread.join()
    else:
        _lcdLoopCondition = False

def startUpdateLCD(fmt = "", fromFile = False):
    global _lcdThread
    global _lcdLoopCondition

    if fromFile:
        with open(const.lcdTextFile,"r") as f:
            fmt = f.read()
    else:
        with open(const.lcdTextFile,"w") as f:
            f.write(fmt)


    if _lcdLoopCondition:
        stopLCD()
    joinLCD()

    _lcdLoopCondition = True
    _lcdThread = Thread(target=lambda : _startLCD(fmt))
    _lcdThread.start()
    print("lcd started")

def getLCDFMT():
    global _fmt
    return _fmt

def toggleLCDBacklight():
    toggleBacklight()
