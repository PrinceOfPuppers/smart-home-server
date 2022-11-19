import schedule
from typing import Union
from queue import Queue, Empty
from threading import Thread
import os
import json
import time

from helpers import clearQueue

from handlers import _addJob, _removeJob, _updateJob, _enableDisableJob, _getJobPath


_scheduleEditQueue      = Queue()
_schedulerLoopCondition = False

def addJob(scheduledJob:dict):
    global _scheduleEditQueue
    _scheduleEditQueue.put(lambda :_addJob(scheduledJob))


def removeJob(id: str):
    global _scheduleEditQueue
    _scheduleEditQueue.put(lambda :_removeJob(id))

def updateJob(id: str, newScheduledJob:dict):
    global _scheduleEditQueue
    _scheduleEditQueue.put(lambda :_updateJob(id, newScheduledJob))

def getJobFromFile(id: str) -> Union[dict, None]:
    path = _getJobPath(id)
    if os.path.exists(path):
        with open(path) as f:
            res = json.load(f)
        return res
    return None

def getJob(id: str) -> Union[dict, None]:
    jobs = schedule.get_jobs(id)
    if len(jobs) > 1:
        raise Exception("Multiple jobs with same id")
    if len(jobs) == 0:
        return None
    job = jobs[0]
    assert job.job_func is not None
    return job.job_func.args[0]

def getJobs():
    jobs = []
    for j in schedule.get_jobs():
        assert j.job_func is not None
        jobs.append(j.job_func.args[0])
    return jobs

def enableDisableJob(id: str, enable:bool):
    global _scheduleEditQueue
    _scheduleEditQueue.put(lambda :_enableDisableJob(id, enable))

def _schedulerLoop():
    global _schedulerLoopCondition
    global _scheduleEditQueue

    while _schedulerLoopCondition:
        while _scheduleEditQueue.qsize() != 0:
            try:
                edit = _scheduleEditQueue.get(block=False)
            except Empty:
                break
            edit()

        schedule.run_pending()
        
        # blocking with 1 second timeout (rather than sleeping)
        try:
            edit = _scheduleEditQueue.get(block=True, timeout=1)
        except Empty:
            continue
        edit()

_schedulerThread = None

def startScheduler():
    global _schedulerLoopCondition
    global _scheduleEditQueue
    global _schedulerThread
    if _schedulerLoopCondition:
        raise Exception("Scheduler Already Running")

    clearQueue(_scheduleEditQueue)
    _schedulerThread = Thread(target=_schedulerLoop)
    _schedulerThread.start()


def stopScheduler():
    global _schedulerLoopCondition
    global _schedulerThread

    if _schedulerThread is not None and _schedulerThread.is_alive():
        _schedulerLoopCondition = False
        _schedulerThread.join()
    else:
        _schedulerLoopCondition = False


while True:
    schedule.run_pending()
    time.sleep(1)

