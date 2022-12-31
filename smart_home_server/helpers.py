from queue import Queue
import requests
import string
import time
from multiprocessing import JoinableQueue

import smart_home_server.constants as const
from typing import Union

def clearQueue(q):
    while not q.empty():
        q.get()

def padZeros(num, length):
    numStr = str(num)
    return f'{"0"*(length - len(numStr))}{numStr}' if len(numStr) < length else numStr


def padChar(s, c, length):
    s = str(s)
    res = f'{s}{c*(length - len(s))}' if len(s) < length else s
    return res

def addDefault(data:dict, key:str, val):
    if key not in data:
        data[key] = val

def getAtTime(scheduledJob:dict):
    # formats:
    # seconds   -> None
    # minutes   -> :SS
    # hours     -> MM:SS
    # otherwise -> HH:MM:SS

    hasSeconds = "atSeconds" in scheduledJob
    hasMinutes = "atMinutes" in scheduledJob
    hasHours   = "atHours"   in scheduledJob

    seconds = padZeros(scheduledJob["atSeconds"], 2) if hasSeconds else "00"
    minutes = padZeros(scheduledJob["atMinutes"], 2) if hasMinutes else "00"
    hours   = padZeros(scheduledJob["atHours"]  , 2) if hasHours   else "00"

    u = scheduledJob['unit']
    if u == 'seconds':
        return None

    s = f':{seconds}'

    if u == 'minute':
        if hasSeconds:
            return s
        return None

    s = f"{minutes}" + s
    if u == 'hours':
        if hasSeconds or hasMinutes:
            return s
        return None

    s = f"{hours}:" + s
    if hasSeconds or hasMinutes or hasHours:
        return s
    return None



def waitUntil(conditionCb, period = 0.01):
  while True:
    if conditionCb(): 
        return
    time.sleep(period)


def roundTimeStr(s):
    # hh:mm:ss -> hh:mm

    x = s.split(':')
    for i in range(len(x)):
        x[i] = int(x[i])

    if x[0] >= 30:
        x[1] += 1
    if x[1] == 60:
        x[1] = 0
        x[2] += 1
    if x[2] == 24:
        x[2] = 0

    return f'{padZeros(x[2], 2)}:{padZeros(x[1], 2)}'
