from smart_home_server.handlers.graphs.helpers import _startGraphs, _deleteGraph, _createGraph, _graphLock, _overwriteGraph, _getGraph, _getGraphs, \
                                                        GraphAlreadyExists, GraphDoesNotExist, DatasourceDoesNotExist, _updateGraph, _stopGraphs

from smart_home_server.handlers.graphs.runtime import generateFigure


def createGraph(name:str, datasource:str, timeHours:int):
    with _graphLock:
        _createGraph(name, datasource, timeHours)

def deleteGraph(id: str):
    with _graphLock:
        _deleteGraph(id)

def updateGraph(id: str, newName = None, newDatasource= None, newTimeHours = None):
    with _graphLock:
        _updateGraph(id, newName, newDatasource, newTimeHours)

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
