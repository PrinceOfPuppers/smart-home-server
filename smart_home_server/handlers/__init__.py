import smart_home_server.constants as const
from uuid import uuid4
from smart_home_server.handlers.presser import presserAppend
from smart_home_server.handlers.lcd import updateLCDFromJobData
from smart_home_server.hardware_interfaces.reboot import reboot
from smart_home_server.handlers.macros import macroExists, getMacro
from time import sleep
from smart_home_server.errors import currentErrors
from threading import Thread, Lock, Event
from datetime import datetime, timedelta

def validateDo(do:dict):
    try:
        type = do['type']
        data = do['data']

        if type == 'press':
            remote = data['remote']
            ch = data['channel']
            if not remote in const.remotes:
                return False
            max = len(const.remotes[remote]) - 1
            min = 0
            if ch < min or ch > max:
                return f"Invalid Channel: {ch} for Remote: {remote} (min: {min}, max: {max})"
        elif type == 'reboot':
            return ""
        elif type == 'lcd':
            return ""
        elif type == 'delay':
            return ""
        elif type == 'macro':
            if not macroExists(data['id']):
                return f"Macro Does Not Exist: {data['id']}"
            return ""

        else:
            print(f"Invalid Job Type '{do}'")
            return "Invalid Job Type"
    except:
        return "Invalid Job"


def validateJob(job:dict):
    # adds additional sanatization not done by schema
    if not 'do' in job:
        return "Job Must Contain 'do'"
    return validateDo(job['do'])


def runJob(job:dict):
    try:
        # job must contain key 'do'
        if 'enabled' in job and not job['enabled']:
            return

        do   = job['do']
        type = do['type']
        data = do['data']

        if type == 'press':
            presserAppend(data)
        elif type == 'lcd':
            updateLCDFromJobData(data)
        elif type == 'reboot':
            reboot()
        elif type == 'macro':
            runMacro(data['id'])
        else:
            raise Exception(f"Invalid Job Type '{do}'")
    except Exception as e:
        print(f'Job Run Error:', repr(e))
        currentErrors['Last_Job_Run_Err'] = f'{datetime.now().strftime("%b %d %H:%M:%S")} {repr(e)}'



_activeDelays:dict = {}
_activeDelayLock = Lock()

def getDelays():
    res = {}
    with _activeDelayLock:
        for id in _activeDelays:
            res[id] = _activeDelays[id].copy()

    for id in res:
        res[id].pop('wait')
        res[id].pop('cancelFlag')
    return res


def cancelSkipDelay(id, cancel:bool = True):
    # if not cancel, just skip it
    with _activeDelayLock:
        if not id in _activeDelays:
            return
        d = _activeDelays[id]
        d['cancelFlag'] = cancel
        d['wait'].set()


def _handleMacroDelay(delay, name):
    id = str(uuid4())
    wait = Event()
    with _activeDelayLock:
        now = datetime.now()
        end = now + timedelta(seconds=delay)
        _activeDelays[id] = {'name': name, 'start': now.isoformat(), 'end': end.isoformat(), 'wait': wait, 'cancelFlag': False}
    wait.wait(delay)
    with _activeDelayLock:
        return _activeDelays.pop(id)['cancelFlag']


def _runMacroSequence(sequence, name, delay = 0):
    global _activeDelays

    if len(sequence) == 0:
        return
    if delay > 0:
        # if cancelled end sequence
        if _handleMacroDelay(delay, name):
            return

    for i,item in enumerate(sequence):
        if item['type'] == 'delay':
            data = item['data']
            seconds = data['seconds'] + data['minutes']*60 + data['hours']*60*60
            t = Thread(target= lambda: _runMacroSequence(sequence[i+1:], name, delay = seconds))
            t.start()
            break
        else:
            runJob({'do': item})

def runMacro(id):
    macro = getMacro(id)
    name = macro['name']
    sequence = macro['sequence']
    print(f"Running Macro: {name}")
    _runMacroSequence(sequence, name)


