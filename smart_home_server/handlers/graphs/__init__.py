from threading import Lock

from smart_home_server.handlers.graphs.helpers import _startGraphs, _deleteGraph, _createGraph, _getGraph, _getGraphs, \
                                                        GraphAlreadyExists, GraphDoesNotExist, DatasourceDoesNotExist, _stopGraphs
from smart_home_server.handlers.graphs.runtime import generateFigure

_graphLock = Lock()

def createGraph(datasource:str, timeHours:int, color:str):
    with _graphLock:
        _createGraph(datasource, timeHours, color)

def deleteGraph(id: str):
    with _graphLock:
        _deleteGraph(id)

def getGraph(id:str):
    with _graphLock:
        return _getGraph(id)

def getGraphs():
    with _graphLock:
        return _getGraphs()


def startGraphs():
    with _graphLock:
        _startGraphs()

def stopGraphs():
    with _graphLock:
        _stopGraphs()
