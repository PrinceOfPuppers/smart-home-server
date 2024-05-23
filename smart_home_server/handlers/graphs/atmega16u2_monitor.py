from smart_home_server.hardware_interfaces.atmega16u2_monitor import await_connection, requestInfo, sendFrame, rgb_to_16_bit
import smart_home_server.constants as const
from smart_home_server.helpers import clearQueue


import hid
from matplotlib.backends.backend_agg import FigureCanvas
from matplotlib.figure import Figure
from matplotlib import rcParams
from dataclasses import dataclass
from queue import Queue,Empty
from threading import Thread
from datetime import datetime
from typing import Callable, Union

_monitorQueue = Queue(1)
_monitorLoopCondition = False
_monitorThread = None

_backlight = 0

px = 1/rcParams['figure.dpi']


def _monitor_loop(h:hid.Device, sequenceCb:Callable[[], int]):
    global _backlight

    seq = sequenceCb()
    x = requestInfo(h)
    if x is None:
        # TODO: error condition
        _monitorLoopCondition = False
        return
        
    width, height, chunckSize, _backlight = x

    x = None
    while seq == sequenceCb():
        try:
            x = _monitorQueue.get(block=True, timeout=const.threadPollingPeriod)
            if isinstance(x, Figure):
                x.set_figheight(height*px)
                x.set_figwidth(width*px)

                c = FigureCanvas(x)
                c.draw()
                b = rgb_to_16_bit(c.tostring_rgb())

                sendFrame(h, b, chunckSize)
                
            # Currently unused
            elif isinstance(x, int):
                # clamp x between 0 and 255
                x = 255 if x > 255 else 0 if x < 0 else x
                # TODO send backlight

        except Empty:
            pass
    # for quick disconnect reconnects, store last frame so monitor is not black on reconnect
    # will not overwrite existing frame in queue
    if x is not None and _monitorQueue.empty():
        _monitorQueue.put(x)


def sendFigureToMonitor(fig):
    # we want the queue to only hold the most recent frame
    clearQueue(_monitorQueue)
    _monitorQueue.put(fig)

def stopMonitorManager():
    global _monitorLoopCondition
    global _monitorThread
    _monitorLoopCondition = False

def joinMonitorManager():
    global _monitorLoopCondition
    global _monitorThread

    if _monitorThread is not None and _monitorThread.is_alive():
        _monitorLoopCondition = False
        _monitorThread.join()
    else:
        _monitorLoopCondition = False

def startMonitorManager():
    global _monitorLoopCondition
    global _monitorManagerJobQueue
    global _monitorThread

    if _monitorLoopCondition:
        raise Exception("Sub Loop Already Running")

    joinMonitorManager()

    _monitorLoopCondition = True
    _monitorThread = Thread(target = lambda : await_connection(lambda: _monitorLoopCondition, _monitor_loop, const.a16u2monitorVid, const.a16u2monitorPid))
    _monitorThread.start()
    print("monitor loop started")
