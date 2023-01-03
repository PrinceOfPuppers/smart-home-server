from uuid import uuid4
import os
import json

from smart_home_server.api import runJob
import smart_home_server.constants as const
from smart_home_server.handlers.subscribeManager import subscribe

from typing import Dict


def _getTriggersPath(id:str):
    return f'{const.triggeredJobFolder}/{id}.json'

class RunningTriggerData:
    def __init__(self, triggerJob:dict):
        self.subscribed = False
        self.triggerJob = triggerJob
        id = str(uuid4()) if 'id' not in triggerJob else triggerJob['id']
        self.triggerJob['id'] = id

        self._prevCondition = False

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
        t.serialize()
        if not t.triggerJob['enabled']:
            return t
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
        stopSig = not self.triggerJob['enabled']
        if stopSig:
            self.subscribed = False
        return stopSig

    def _errorCb(self, e):
        print(f"Trigger Job {self.triggerJob['name']} Error: {repr(e)}", flush=True)
        
    def stop(self):
        self.triggerJob['enabled'] = False

    def start(self):
        if self.subscribed:
            print(f"Trigger Job {self.triggerJob['name']} Attempted to Start While Already Running", flush=True)
            return

        self.subscribed = True
        self._prevCondition = False

        if not self.triggerJob['enabled']:
            print(f"Trigger Job {self.triggerJob['name']} Attempted to Start While Being Disabled", flush=True)
            return

        var1 = self.triggerJob['firstVar']['value']

        if self.triggerJob['secondVar']['type'] == 'dataSource':
            var2 = self.triggerJob['secondVar']['value']
            subscribe([var1, var2], self._do, self._stopCb, self._errorCb)
        else:
            subscribe([var1], self._do, self._stopCb, self._errorCb)

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
            print(f"Trigger Job {self.triggerJob['name']} Has a None Value: var1={var1} var2={var2}", flush=True)


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


    def delete(self):
        self.stop()
        path = _getTriggersPath(self.getId())
        if os.path.exists(path):
            os.remove(path)

    def serialize(self):
        with open(_getTriggersPath(self.getId()), 'w') as f:
            f.write(json.dumps(self.triggerJob))
        pass

_loaded = False

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
        if not t.subscribed:
            t.start()
    else:
        t.disable()

def _loadTriggers():
    global _triggers
    global _loaded
    print("Loading Triggers")
    for t in _triggers.values():
        t.stop()
    _triggers.clear()

    dir = os.listdir(const.triggeredJobFolder)
    for p in dir:
        path = f'{const.triggeredJobFolder}/{p}'
        t = RunningTriggerData.deserialize(path)
        _triggers[t.getId()] = t
        if t.triggerJob['enabled']:
            t.start()

    print("Triggers Loaded")
    _loaded = True

def _updateTriggerName(id: str, name:str):
    global _triggers
    global _loaded

    if not _loaded:
        _loadTriggers()

    if not id in _triggers:
        return
    _triggers[id].updateName(name)


def _getTrigger(id: str):
    global _triggers
    global _loaded

    if not _loaded:
        _loadTriggers()

    if id not in _triggers:
        return None

    t = _triggers[id]
    return t.triggerJob

def _getTriggers():
    global _triggers
    global _loaded

    if not _loaded:
        _loadTriggers()

    res = []
    for id in _triggers.keys():
        if id not in _triggers:
            continue
        res.append(_triggers[id].triggerJob)

    res.sort(key = lambda element: element['name'])
    return res

