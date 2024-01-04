from uuid import uuid4
from threading import Thread, Lock, Event
from datetime import datetime, timedelta

from smart_home_server.handlers.presser import presserAppend, getRemoteById
from smart_home_server.hardware_interfaces.reboot import reboot
from smart_home_server.hardware_interfaces.update import update
from smart_home_server.handlers.macros import macroExists, getMacro
from smart_home_server.handlers.lcd import getLcd, overwriteLcd, LcdDoesNotExist
from smart_home_server.errors import currentErrors

from smart_home_server.handlers.logs import jobLog

def validateDo(do:dict):
    try:
        type = do['type']
        data = do['data']

        if type == 'press':
            id = data['id']
            ch = data['channel']
            remote = getRemoteById(id, throw=False)
            if remote is None:
                return False
            max = len(remote['channels']) - 1
            min = 0
            if ch < min or ch > max:
                return f"Invalid Channel: {ch} for Remote ID: {id} (min: {min}, max: {max})"
        elif type == 'reboot':
            return ""
        elif type == 'update':
            return ""
        elif type == 'lcd':
            num = data["num"]
            try:
                getLcd(num)
            except LcdDoesNotExist:
                return f"Lcd: {data['num']} Does Not Exist"
            if 'backlight' in data and data['backlight'] not in ["toggle", "on", "off"]:
                return f"Unknown Lcd Backlight Command: {data['backlight']}"
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


def logJob(type, data):
    jobLog.append(f"{datetime.now().strftime('%b %d %H:%M:%S')} -> {type}\n  data: {data}")

def runJob(job:dict):
    # job must contain key 'do' which must have 'type' and 'data'

    try:
        if 'enabled' in job and not job['enabled']:
            return

        do   = job['do']
        type = do['type']
        data = do['data']

        if type == 'press':
            presserAppend(data)

        elif type == 'lcd':
            overwriteLcd(data["num"], data)
        elif type == 'reboot':
            reboot()
        elif type == 'update':
            update()
        elif type == 'macro':
            runMacro(data['id'])
        else:
            raise Exception(f"Invalid Job Type '{do}'")

        # runMacro also logs
        if type != 'macro':
            logJob(type, data)

        #jobLog.append(f"{datetime.now().strftime('%b %d %H:%M:%S')} -> {type}\n  data: {data}")
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
    logJob('macro', {'name': name, 'id': id})
    _runMacroSequence(sequence, name)

