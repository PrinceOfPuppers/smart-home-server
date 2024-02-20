from threading import Lock
import os
import json
from uuid import uuid4

import smart_home_server.constants as const
from smart_home_server.data_sources import getPollingPeriod
from smart_home_server.handlers.graphs.runtime import _addPoint, GraphAlreadyExists, GraphDoesNotExist, _startGraphPlotting, _stopGraphPlotting

class DatasourceDoesNotExist(Exception):
    pass

_graphLock = Lock()
_graphCache:dict = {}

def _getGraphPath(id:str):
    return f'{const.graphsFolder}/{id}.json'

def _saveGraph(graph:dict, id = None):
    if id == None or id.strip() == '':
        id = str(uuid4())
        graph['id'] = id
    _graphCache[id] = graph

    path = _getGraphPath(id)
    if os.path.exists(path):
        raise GraphAlreadyExists()

    with open(path, "w") as f:
        f.write(json.dumps(graph))

    return id


def _deleteGraph(id: str):
    _stopGraphPlotting(id)

    if id in _graphCache:
        _graphCache.pop(id)
    path = _getGraphPath(id)
    if os.path.exists(path):
        os.remove(path)
        return
    raise GraphDoesNotExist()

def _getGraph(id:str):
    if id in _graphCache:
        return _graphCache[id]

    path = _getGraphPath(id)
    if not os.path.exists(path):
        raise GraphDoesNotExist()

    with open(path, "r") as f:
        j = json.loads(f.read())

    j['id'] = id
    _graphCache[id] = j
    return j

def _getGraphs():
    dir = os.listdir(const.graphsFolder)
    graphs = []
    for p in dir:
        graph = _getGraph(p.strip(".json"))
        if graph is None:
            continue
        graphs.append(graph)
    return graphs


def _getNumSamples(datasource:str, timeHours:int):
    pollingPeriod = getPollingPeriod(datasource)
    if pollingPeriod is None:
        raise DatasourceDoesNotExist()

    numSamples = round((timeHours * 60 * 60) / pollingPeriod)
    return numSamples if numSamples >= 2 else 2 # min graph size is 3 samples

def _createGraph(datasource:str, timeHours:int):
    numSamples = _getNumSamples(datasource, timeHours)

    graph = {"datasource": datasource, "numSamples": numSamples, "timeHours": timeHours}
    id = _saveGraph(graph)
    _startGraphPlotting(id, numSamples, datasource)


def _startGraphs():
    graphs = _getGraphs()
    for graph in graphs:
        _startGraphPlotting(graph["id"], graph["numSamples"], graph["datasource"])


def _stopGraphs():
    graphs = _getGraphs()
    for graph in graphs:
        _stopGraphPlotting(graph["id"])

