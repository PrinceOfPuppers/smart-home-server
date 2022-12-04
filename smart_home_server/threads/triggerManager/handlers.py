from uuid import uuid4
import os
import json
from threading import Thread

from smart_home_server.api import runJob
from smart_home_server.data_sources.polling import polledUpdate
import smart_home_server.constants as const

from typing import Dict


def _getTriggersPath(id:str):
    return f'{const.triggeredJobFolder}/{id}.json'

class RunningTriggerData:
    def __init__(self, triggerJob):
        self.triggerJob = triggerJob
        id = str(uuid4()) if 'id' not in triggerJob else triggerJob['id']
        self.triggerJob['id'] = id

        self._prevCondition = False
        self._manualStop = False

        self.thread = None

    def getId(self):
        return self.triggerJob['id']

    @classmethod
    def deserialize(cls, path):
        with open(path, 'r') as f:
            triggerJob = json.load(f)
        return cls(triggerJob)

    @classmethod
    def createNewTriggerAndStart(cls, triggerJob):
        t = cls(triggerJob)
        if not t.triggerJob['enabled']:
            t.serialize()
            return t
        t.enable()
        t.start()
        return t

    def enable(self):
        self.triggerJob['enabled'] = True
        self.serialize()

    def disable(self):
        self.triggerJob['enabled'] = False
        self.serialize()

    def updateName(self, name):
        self.triggerJob['name'] = name
        self.serialize()

    def _stopCb(self):
        return self.triggerJob['enabled'] and not self.manualStop

    def _errorCb(self, e):
        print(f"Trigger Job {self.triggerJob['name']} Error: {repr(e)}", flush=True)
        
    def join(self):
        self.triggerJob['enabled'] = False
        if self.thread is not None:
            self.thread.join()
            self.thread = None

    # will restart if already enabled
    def start(self):
        self._manualStop = False
        self._prevCondition = False
        if self.thread is not None:
            self.thread.join()
            self.thread = None

        if not self.triggerJob['enabled']:
            print(f"Trigger Job {self.triggerJob['name']} Attempted to Start While Being Disabled", flush=True)
            return

        var1 = self.triggerJob['firstVar']['value']

        if self.triggerJob['secondVar']['type'] == 'dataSource':
            var2 = self.triggerJob['secondVar']['value']
            l = polledUpdate([var1, var2], self._do, self._stopCb, self._errorCb)
        else:
            l = lambda: polledUpdate([var1], self._do, self._stopCb, self._errorCb)

        self.thread = Thread(target=l)
        self.thread.start()

    def _do(self, values):
        if not self.triggerJob['enabled']:
            print(f"Trigger Job: {self.triggerJob['name']} Called When Disabled", flush=True)
            return


        var1 = self.triggerJob['firstVar']['value']
        if not var1 in values:
            print(f"Trigger Job {self.triggerJob['name']} Missing Value: {var1}", flush=True)
            return

        var1Value = values[var1]

        var2 = self.triggerJob['secondVar']['value']
        if self.triggerJob['secondVar']['type'] == 'dataSource':
            if not var1 in values:
                print(f"Trigger Job {self.triggerJob['name']} Missing Value: {var2}", flush=True)
                return
            var2Value = values[var2]
        else:
            var2Value = var2

        if var1Value is None or var2Value is None:
            print(f"Trigger Job {self.triggerJob['name']} Has a None Value: {var1=} {var2=}", flush=True)


        negated = self.triggerJob['negated']
        comparison = self.triggerJob['comparison']

        # try to convert to float/int
        if isinstance(var1Value,str):
            if var1Value.isdigit():
                var1Value = int(var1Value)
            else:
                try:
                    var1Value = float(var1Value)
                except:
                    pass

        # try to convert to float/int
        if isinstance(var2Value,str):
            if var2Value.isdigit():
                var2Value = int(var2Value)
            else:
                try:
                    var2Value = float(var2Value)
                except:
                    pass

        # if one is still str, make them both str
        if isinstance(var1Value,str) != isinstance(var2Value,str):
            var1Value = str(var1Value)
            var2Value = str(var2Value)

        print(type(var1Value), type(var2Value))
        condition = False
        if comparison == '=':
            condition = (var1Value == var2Value) or str(var1Value).lower() == str(var2Value).lower()
        elif comparison == '>':
            condition = var1Value > var2Value
        elif comparison == '<':
            condition = var1Value < var2Value
        elif comparison == '>=':
            condition = var1Value >= var2Value
        elif comparison == '<=':
            condition = var1Value <= var2Value
        elif comparison == 'contains':
            condition = str(var2Value).lower() in str(var1Value).lower()

        condition = condition != negated

        # DeBouncing: if we triggered the event previously, dont retrigger event
        if self._prevCondition:
            self._prevCondition = condition
            return
        self._prevCondition = condition

        if condition:
            runJob(self.triggerJob)


    def manualStop(self):
        self._manualStop = True

    def delete(self):
        self.join()
        path = _getTriggersPath(self.getId())
        if os.path.exists(path):
            os.remove(path)

    def serialize(self):
        with open(_getTriggersPath(self.getId()), 'w') as f:
            f.write(json.dumps(self.triggerJob))
        pass


# TODO: stop all triggers
_triggers:Dict[str,RunningTriggerData] = {}
def _addTrigger(triggerJob:dict):
    global _triggers
    t = RunningTriggerData.createNewTriggerAndStart(triggerJob)
    _triggers[t.getId()] = t

def _removeTrigger(id: str):
    global _triggers
    if not id in _triggers:
        return
    t = _triggers.pop(id)
    t.delete()


def _enableDisableTrigger(id: str, enable=True):
    global _triggers
    if not id in _triggers:
        return
    t = _triggers[id]

    if enable:
        t.enable()
        t.start()
    else:
        t.disable()

def _loadTriggers():
    global _triggers
    for t in _triggers.values():
        t.manualStop()
    for t in _triggers.values():
        t.join()
    _triggers.clear()

    dir = os.listdir(const.triggeredJobFolder)
    for p in dir:
        path = f'{const.triggeredJobFolder}/{p}'
        t = RunningTriggerData.deserialize(path)
        _triggers[t.getId()] = t
        if t.triggerJob['enabled']:
            t.start()

def _updateTriggerName(id: str, name:str):
    global _triggers
    if not id in _triggers:
        return
    _triggers[id].updateName(name)


def _getTrigger(id: str, triggerOut:list, conditionOut:list):
    global _triggers
    if id not in _triggers:
        return None

    t = _triggers[id]
    triggerOut.append(t.triggerJob)
    conditionOut[0] = True

def _getTriggers(triggerOut:list, conditionOut:list):
    global _triggers
    res = []
    for id in _triggers.keys():
        if id not in _triggers:
            continue
        triggerOut.append(_triggers[id].triggerJob)

    triggerOut.sort(key = lambda element: element['name'])
    conditionOut[0] = True
    return res
