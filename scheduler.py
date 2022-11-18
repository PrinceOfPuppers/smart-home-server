import schedule
from typing import Union, Callable
from queue import Queue
from uuid import uuid4
import os
from dataclasses import dataclass

import json

from presser import presserAppend
import constants as const

_scheduleEditQueue = Queue()

@dataclass
class QueuedJob:
    taskJson: dict

    cb: Callable

    

#input tasks will not have an uuid
{
    "name": "test job",
    "id": "asdfakhjfqkhlk",
    "enabled": True,
    "every": 2,
    "unit": "hours",
    "at": "HH:MM:SS",

    "do": {
        "type": "press",
        "data": {
            "channel": 1,
            "value": False
        }

    }
}

def _runJob(scheduledJob:dict):
    j = scheduledJob['do']
    if j['type'] == 'press':
        presserAppend(j['data'])
    else:
        raise Exception(f"Invalid Job Type '{j['do']}'")


def getJobPath(id:str):
    return f'{const.schedulerJobFolder}/{id}.json'


def parseTask(scheduledJob:dict):
    if "every" in scheduledJob:
        s = schedule.every(scheduledJob["every"])
    else:
        s = schedule.every()
    s = s.__getattribute__(scheduledJob['unit'])

    if "at" in scheduledJob:
        s = s.at(scheduledJob['at'])

    return s

def _storeJob(scheduledJob: dict, id: str):
    scheduledJob['id'] = id
    with open(getJobPath(id), 'a') as f:
        f.write(json.dumps(scheduledJob))
    return id



def _addJob(scheduledJob:dict):
    s = parseTask(scheduledJob)
    id = str(uuid4())
    _storeJob(scheduledJob, id)
    s.tag(id)
    s.job(_runJob, scheduledJob=scheduledJob)

def addJob(scheduledJob:dict):
    global _scheduleEditQueue
    _scheduleEditQueue.put(lambda :_addJob(scheduledJob))


def _removeJob(id: str):
    path = getJobPath(id)
    if os.path.exists(path):
        os.remove(path)

    schedule.clear(id)

def removeJob(id: str):
    global _scheduleEditQueue
    _scheduleEditQueue.put(lambda :_removeJob(id))


def _updateJob(id: str, newScheduledJob:dict):
    if 'id' in newScheduledJob:
        newScheduledJob['id'] = id

    _removeJob(id)
    _addJob(newScheduledJob)

def updateJob(id: str, newScheduledJob:dict):
    global _scheduleEditQueue
    _scheduleEditQueue.put(lambda :_updateJob(id, newScheduledJob))

def getJobFromFile(id: str) -> Union[dict, None]:
    path = getJobPath(id)
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

def _enableDisableJob(id: str, enable:bool):
    jobs = schedule.get_jobs(id)
    if len(jobs) > 1:
        raise Exception("Multiple jobs with same id")
    if len(jobs) == 0:
        return
    job = jobs[0]
    assert job.job_func is not None
    scheduledJob = job.job_func.args[0]

    if scheduledJob['enabled'] == enable:
        return
    
    scheduledJob['enabled'] = enable
    _updateJob(id, scheduledJob)

def enableDisableJob(id: str, enable:bool):
    global _scheduleEditQueue
    _scheduleEditQueue.put(lambda :_enableDisableJob(id, enable))






while True:
    schedule.run_pending()
    time.sleep(1)

