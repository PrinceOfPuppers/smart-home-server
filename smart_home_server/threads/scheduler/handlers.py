import schedule
from uuid import uuid4
import os
import json

from smart_home_server.threads.presser import presserAppend
import smart_home_server.constants as const


def _runJob(scheduledJob:dict):
    j = scheduledJob['do']
    if not j['enabled']:
        return

    if j['type'] == 'press':
        presserAppend(j['data'])
    else:
        raise Exception(f"Invalid Job Type '{j['do']}'")


def _getJobPath(id:str):
    return f'{const.schedulerJobFolder}/{id}.json'


def _parseTask(scheduledJob:dict):
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
    with open(_getJobPath(id), 'a') as f:
        f.write(json.dumps(scheduledJob))
    return id

def _addJob(scheduledJob:dict):
    s = _parseTask(scheduledJob)
    id = str(uuid4())
    _storeJob(scheduledJob, id)
    s.tag(id)
    s.job(_runJob, scheduledJob=scheduledJob)

def _removeJob(id: str):
    path = _getJobPath(id)
    if os.path.exists(path):
        os.remove(path)

    schedule.clear(id)

def _updateJob(id: str, newScheduledJob:dict):
    if 'id' in newScheduledJob:
        newScheduledJob['id'] = id

    _removeJob(id)
    _addJob(newScheduledJob)

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

