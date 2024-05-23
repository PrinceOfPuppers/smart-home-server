from threading import Lock

from smart_home_server.handlers.graphs.helpers import _startGraphs, _deleteGraph, _createGraph, _getGraph, _getGraphs, \
                                                        GraphAlreadyExists, GraphDoesNotExist, DatasourceDoesNotExist, _stopGraphs
from smart_home_server.handlers.graphs.runtime import generateFigure, _putOnMonitor, _getOnMonitor
from smart_home_server.handlers.graphs.atmega16u2_monitor import startMonitorManager, stopMonitorManager, joinMonitorManager
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
        startMonitorManager()

def stopGraphs():
    with _graphLock:
        _stopGraphs()
        stopMonitorManager()

def joinGraphs():
    with _graphLock:
        joinMonitorManager()

def putOnMonitor(id:str):
    with _graphLock:
        _putOnMonitor(id)

def getOnMonitor():
    with _graphLock:
        return _getOnMonitor()
