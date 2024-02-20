from smart_home_server.handlers.graphs.helpers import _startGraphs, _deleteGraph, _createGraph, _graphLock, _getGraph, _getGraphs, \
                                                        GraphAlreadyExists, GraphDoesNotExist, DatasourceDoesNotExist, _stopGraphs

from smart_home_server.handlers.graphs.runtime import generateFigure


def createGraph(datasource:str, timeHours:int):
    with _graphLock:
        _createGraph(datasource, timeHours)

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
