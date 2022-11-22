import schedule
from typing import Union
from queue import Queue, Empty
from threading import Thread
import os
import json

from smart_home_server.helpers import clearQueue
import smart_home_server.constants as const
from smart_home_server.threads.scheduler.handlers import _addJob, _removeJob, _updateJob, _enableDisableJob, _getJobPath, _loadJobs

_scheduleEditQueue      = Queue()
_schedulerLoopCondition = False
_schedulerThread = None

def addJob(scheduledJob:dict):
    global _scheduleEditQueue
    _scheduleEditQueue.put(lambda :_addJob(scheduledJob))


def removeJob(id: str):
    global _scheduleEditQueue
    _scheduleEditQueue.put(lambda :_removeJob(id))

def updateJob(id: str, newScheduledJob:dict):
    global _scheduleEditQueue
    _scheduleEditQueue.put(lambda :_updateJob(id, newScheduledJob))

def loadJobs(clearExisting:bool, overwrite:bool):
    global _scheduleEditQueue
    _scheduleEditQueue.put(lambda :_loadJobs(clearExisting=clearExisting, overwrite=overwrite))


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
        try:
            while _scheduleEditQueue.qsize() != 0:
                try:
                    edit = _scheduleEditQueue.get(block=False)
                except Empty:
                    break
                edit()

            schedule.run_pending()
            
            # blocking with [pollingPeriod] second timeout (rather than sleeping)
            try:
                edit = _scheduleEditQueue.get(block=True, timeout=const.pollingPeriod)
            except Empty:
                continue
            edit()
        except Exception as e:
            print(f"Scheduler Exception: \n{e}")
            continue


def startScheduler():
    global _schedulerLoopCondition
    global _scheduleEditQueue
    global _schedulerThread
    if _schedulerLoopCondition:
        raise Exception("Scheduler Already Running")

    clearQueue(_scheduleEditQueue)
    loadJobs(clearExisting=True, overwrite=True)
    _schedulerLoopCondition = True
    _schedulerThread = Thread(target=_schedulerLoop)
    _schedulerThread.start()
    print("scheduler started")


def stopScheduler():
    global _schedulerLoopCondition
    global _schedulerThread
    _schedulerLoopCondition = False

def joinScheduler():
    global _schedulerLoopCondition
    global _schedulerThread

    if _schedulerThread is not None and _schedulerThread.is_alive():
        _schedulerLoopCondition = False
        _schedulerThread.join()
    else:
        _schedulerLoopCondition = False
    print("scheduler joined")