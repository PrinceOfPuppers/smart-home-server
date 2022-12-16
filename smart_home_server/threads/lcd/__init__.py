import string

import smart_home_server.constants as const
from smart_home_server.hardware_interfaces.lcd import setLCDFMT, printfLCD, toggleBacklight, getLCDFMT, setBacklight
from smart_home_server.threads.subscribeManager import subscribe

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
    s = ""
    last = getLCDFMT().split('\n')
    if 'line1' in data:
        s += data['line1']
    else:
        if len(last) > 0:
            s += last[0]
    if 'line2' in data:
        s += f'\n{data["line2"]}'
    else:
        if len(last) > 1:
            s += f'\n{last[1]}'

    try:
        s.encode('ascii')
    except UnicodeEncodeError:
        return False

    startUpdateLCD(s)
    if 'backlight' in data:
        setLCDBacklight(data['backlight'])

    return True
