import string
from threading import Thread

import smart_home_server.constants as const
from smart_home_server.hardware_interfaces.lcd import setLCDFMT, printfLCD, toggleBacklight, getLCDFMT
from smart_home_server.data_sources.polling import polledUpdate
from smart_home_server.data_sources import dataSources

_lcdThread = None
_lcdLoopCondition = False

def _startLCD():
    global _lcdLoopCondition

    args = {tup[1] for tup in string.Formatter().parse(getLCDFMT()) if tup[1] is not None}

    sources = []
    for s in dataSources:
        if 'values' not in s:
            continue

        keys = args.intersection({key for key in s['values'].keys()})

        if len(keys) == 0:
            continue

        sources.append({
            'pollingPeriod': s['pollingPeriod'],
            'local': s['local'],
            'values': {key: s['values'][key] for key in keys}
        })

    polledUpdate(\
         sources, 
         lambda values:printfLCD(values), 
         lambda: _lcdLoopCondition, 
         lambda e: print(f"LCD Exception: \n{e}", flush=True)
     )


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

    setLCDFMT(fmt)


    if _lcdLoopCondition:
        stopLCD()
    joinLCD()

    _lcdLoopCondition = True
    _lcdThread = Thread(target=lambda : _startLCD())
    _lcdThread.start()
    print("lcd started")

def toggleLCDBacklight():
    toggleBacklight()
