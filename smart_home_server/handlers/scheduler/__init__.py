import schedule
from typing import Union
from threading import Lock, Thread
import os
import json
from datetime import datetime
from time import sleep

import smart_home_server.constants as const
from smart_home_server.handlers.scheduler.helpers import _addJob, _removeJob, _enableDisableJob, _getJobPath, _loadJobs, _getJobs, _getJob, _updateJobName, \
                                                         JobAlreadyExists, JobDoesNotExist

_schedulerLoopCondition = False
_schedulerThread        = None

_schedulerLock = Lock()

def addJob(scheduledJob:dict):
    with _schedulerLock:
        _addJob(scheduledJob)


def removeJob(id: str):
    with _schedulerLock:
        _removeJob(id)

def updateJobName(id: str, name:str):
    with _schedulerLock:
        _updateJobName(id, name)

def loadJobs(clearExisting:bool, overwrite:bool):
    with _schedulerLock:
        Thread(target = lambda: _loadJobs(clearExisting=clearExisting, overwrite=overwrite), daemon=True).start()


def getJobFromFile(id: str) -> Union[dict, None]:
    path = _getJobPath(id)
    if os.path.exists(path):
        with open(path) as f:
            res = json.load(f)
        return res
    raise JobDoesNotExist()

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
