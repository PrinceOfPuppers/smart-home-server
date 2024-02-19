from smart_home_server.handlers.graphs.helpers import _startGraphs, _deleteGraph, _createGraph, _graphLock, _overwriteGraph, _getGraph, _getGraphs, \
                                                        GraphAlreadyExists, GraphDoesNotExist

def createGraph(graph:dict):
    with _graphLock:
        _createGraph(graph)


def deleteGraph(id: str):
    with _graphLock:
        _deleteGraph(id)

def overwriteGraph(graph:dict, id: str):
    with _graphLock:
        _overwriteGraph(graph, id)

def getGraph(id:str):
    with _graphLock:
        return _getGraph(id)

def getGraphs():
    with _graphLock:
        return _getGraphs()


def startGraphs():
    with _graphLock:
        _startGraphs()
