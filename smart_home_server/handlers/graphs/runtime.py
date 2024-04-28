from time import time
from dataclasses import dataclass
from matplotlib.figure import Figure
from matplotlib.ticker import FormatStrFormatter
import matplotlib as mpl
import json

from threading import Lock
from typing import Union

import smart_home_server.constants as const
from smart_home_server.handlers.subscribeManager import subscribe
from smart_home_server.handlers.graphs.atmega16u2_monitor import sendFigureToMonitor

textColor = const.colors["white"]
mpl.rcParams['text.color'] = textColor
mpl.rcParams['axes.labelcolor'] = textColor
mpl.rcParams['xtick.color'] = textColor
mpl.rcParams['ytick.color'] = textColor
mpl.rcParams['figure.facecolor'] = const.colors["grey"]
mpl.rcParams['axes.facecolor'] = const.colors["darkGrey"]


class GraphDoesNotExist(Exception):
    pass

class GraphAlreadyExists(Exception):
    pass

@dataclass
class GraphRuntime:
    id:str
    datasource:str
    colorHex:str
    lastUpdated:float
    ts: list
    ys: list
    maxLen: int
    lock:Lock
    onMonitor:bool = False # only 1 graph can be on the monitor
    index:int = 0
    seq:int = 0

_graphRuntimes:dict = {}
_graphRuntimesLock = Lock()


def _addPoint(g:GraphRuntime, value):
    now = time()

    with g.lock:
        # circleBuff mode
        if len(g.ts) == g.maxLen:
            g.ts[g.index] = now
            g.ys[g.index] = value

        # append mode
        else:
            g.ts.append(now)
            g.ys.append(value)

        g.lastUpdated = now

        # increment index
        g.index += 1
        g.index %= g.maxLen

    if g.onMonitor:
        sendFigureToMonitor(generateSmallFigure(g.id))

def _generateFigureHelper(id:str):
    if id not in _graphRuntimes:
        raise GraphDoesNotExist()

    with _graphRuntimesLock:
        g:GraphRuntime = _graphRuntimes[id]
        with g.lock:
            # sort circle buffers
            if len(g.ts) == 0:
                ts = []
                ys = []
                delta = 0
            else:
                ts, ys = zip(*sorted( filter(lambda x: x[0] != None, zip(g.ts, g.ys)) ))
                delta = ts[-1] - ts[0]
            color = g.colorHex
            title = g.datasource

    now = time()


    if delta < 3*60: # 3 minutes
        tlabel = "Seconds"
        relTs = [x-now for x in ts]

    elif delta < 3*60*60: # 3 hours
        tlabel = "Minutes"
        relTs = [(x-now)/60 for x in ts]

    else:
        relTs = [(x-now)/(60*60) for x in ts]
        tlabel = "Hours"

    return relTs, tlabel, ys, color, title

# create new ts with t=0 being now
def generateFigure(id:str):
    relTs, tlabel, ys, color, title = _generateFigureHelper(id)

    fig = Figure()

    axis = fig.add_subplot(1, 1, 1)
    axis.plot(relTs, ys, color=color)
    axis.set_xlabel(f"Time ({tlabel})")
    axis.set_title(title)
    return fig

def generateSmallFigure(id:str):
    import numpy as np
    relTs, tlabel, ys, color, title = _generateFigureHelper(id)

    fig = Figure()
    fig.subplots_adjust(right=0.95, left=0.15)
    fig.suptitle(title + " vs " + tlabel, size=8)
    axis = fig.add_subplot(1, 1, 1)
    axis.plot(relTs, ys, color=color)
    #axis.set_title(title + " vs " + tlabel, pad=3, size=8)
    axis.tick_params(labelsize=6, length=0, color=const.colors["black"], pad=2)
    axis.tick_params(axis="y", pad=1)

    return fig

def _subscribeErrCB(datasource, e:Exception):
    # TODO: add to errors
    print(f"Graph {datasource} Exception: \n{repr(e)}", flush=True)

# stops previously running graph
def _startGraphPlotting(id:str, numSamples:int, datasource:str, color:str):
    with _graphRuntimesLock:
        if id in _graphRuntimes:
            _graphRuntimes[id].seq += 1

        runtime = GraphRuntime(id, datasource, const.colors[color], 0, [], [], numSamples, Lock())

        _graphRuntimes[id] = runtime
        current = runtime.seq

        subscribe(\
             [datasource],
             lambda values:_addPoint(runtime, values[datasource]),
             lambda: current != runtime.seq,
             lambda e: _subscribeErrCB(datasource, e)
         )

def _stopGraphPlotting(id:str):
    with _graphRuntimesLock:
        if id in _graphRuntimes:
            with _graphRuntimes[id].lock:
                _graphRuntimes[id].seq += 1
            _graphRuntimes.pop(id)

# stores prev id to avoid having to iterate through all running graphs
_prevOnMonitorID = None
def _putOnMonitor(id:str, save=True):
    global _prevOnMonitorID
    if _prevOnMonitorID == id:
        return

    with _graphRuntimesLock:
        if not id in _graphRuntimes:
            raise GraphDoesNotExist()

        if _prevOnMonitorID is not None and _prevOnMonitorID in _graphRuntimes:
            _graphRuntimes[_prevOnMonitorID].onMonitor = False

        _graphRuntimes[id].onMonitor = True
        _prevOnMonitorID = id
        with open(const.a16u2MonitorIdFile, "w") as f:
            f.write(json.dumps({"id": id}))
    sendFigureToMonitor(generateSmallFigure(id))


def _getOnMonitor() -> Union[str,None]:
    return _prevOnMonitorID

def _loadOnMonitor():
        with open(const.a16u2MonitorIdFile, "r") as f:
            id = json.loads(f.read())["id"]
            if id:
                _putOnMonitor(id, save=False)
                #print("here")
                #sendFigureToMonitor(generateSmallFigure(id))
                #print("here")



