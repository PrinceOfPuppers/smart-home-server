import string

import smart_home_server.constants as const
from smart_home_server.hardware_interfaces.lcd import setLCDFMT, printfLCD, toggleBacklight, getLCDFMT, setBacklight
from smart_home_server.handlers.subscribeManager import subscribe

# increment to unsub to from current subscribe
_seq = 0

def _startLCD():
    args = [tup[1] for tup in string.Formatter().parse(getLCDFMT()) if tup[1] is not None]
    current = _seq

    subscribe(\
         args, 
         lambda values:printfLCD(values), 
         lambda: current != _seq, 
         lambda e: print(f"LCD Exception: \n{repr(e)}", flush=True)
     )

def startUpdateLCD(fmt = "", fromFile = False):
    global _seq
    _seq += 1

    if fromFile:
        with open(const.lcdTextFile,"r") as f:
            fmt = f.read()
    else:
        with open(const.lcdTextFile,"w") as f:
            f.write(fmt)

    setLCDFMT(fmt)
    _startLCD()
    print("lcd started")

def toggleLCDBacklight():
    toggleBacklight()

def setLCDBacklight(on: bool):
    setBacklight(on)

def updateLCDFromJobData(data:dict):
    if 'backlight' in data:
        setLCDBacklight(data['backlight'])

    s = ""
    last = getLCDFMT().split('\n')

    if not 'lines' in data:
        return

    numLines = min(len(data['lines']), const.lcdLines)

    for i in range(numLines):
        s += data['lines'][i].replace('\n', '')
        s += "\n"

    try:
        s.encode('ascii')
    except UnicodeEncodeError:
        return False

    startUpdateLCD(s)

    return True
