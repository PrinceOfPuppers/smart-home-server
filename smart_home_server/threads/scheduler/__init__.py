import schedule
from typing import Union
from threading import Lock, Thread
import os
import json
from datetime import datetime
from time import sleep

import smart_home_server.constants as const
from smart_home_server.threads.scheduler.handlers import _addJob, _removeJob, _updateJob, _enableDisableJob, _getJobPath, _loadJobs, _getJobs, _getJob

_schedulerLoopCondition = False
_schedulerThread        = None

_schedulerLock = Lock()

def addJob(scheduledJob:dict):
    with _schedulerLock:
        _addJob(scheduledJob)


def removeJob(id: str):
    with _schedulerLock:
        _removeJob(id)

def updateJob(id: str, newScheduledJob:dict):
    with _schedulerLock:
        _updateJob(id, newScheduledJob)

def loadJobs(clearExisting:bool, overwrite:bool):
    with _schedulerLock:
        _loadJobs(clearExisting=clearExisting, overwrite=overwrite)


def getJobFromFile(id: str) -> Union[dict, None]:
    path = _getJobPath(id)
    if os.path.exists(path):
        with open(path) as f:
            res = json.load(f)
        return res
    return None

def getJob(id:str):
    with _schedulerLock:
        return _getJob(id)

def getJobs():
    with _schedulerLock:
        return _getJobs()

def enableDisableJob(id: str, enable:bool):
    with _schedulerLock:
        _enableDisableJob(id, enable)

def _schedulerLoop():
    global _schedulerLoopCondition
    global _scheduleEditQueue

    while _schedulerLoopCondition:
        try:
            with _schedulerLock:
                schedule.run_pending()
        except Exception as e:
            print(f"Scheduler Exception: \n{repr(e)}", flush=True)
        sleep(const.threadPollingPeriod)



def stopScheduler():
    global _schedulerLoopCondition
    _schedulerLoopCondition = False

def joinScheduler():
    global _schedulerLoopCondition
    global _schedulerThread

    if _schedulerThread is not None and _schedulerThread.is_alive():
        _schedulerLoopCondition = False
        _schedulerThread.join()
    else:
        _schedulerLoopCondition = False

def startScheduler():
    global _schedulerLoopCondition
    global _schedulerThread
    if _schedulerLoopCondition:
        raise Exception("Scheduler Already Running")

    joinScheduler()

    print(f"Scheduler Load Time: {datetime.now()}")
    loadJobs(clearExisting=True, overwrite=True)
    _schedulerLoopCondition = True
    _schedulerThread = Thread(target=_schedulerLoop)
    _schedulerThread.start()
    print("scheduler started")
