from smart_home_server.hardware_interfaces.atmega16u2_monitor import await_connection, requestInfo, sendFrame, rgb_to_16_bit
import smart_home_server.constants as const
from smart_home_server.helpers import clearQueue


from matplotlib.backends.backend_agg import FigureCanvas
from matplotlib.figure import Figure
from matplotlib import rcParams
from dataclasses import dataclass
from queue import Queue,Empty
from threading import Thread
from datetime import datetime

_monitorQueue = Queue(1)
_monitorLoopCondition = False
_monitorThread = None

_backlight = 0

px = 1/rcParams['figure.dpi']


def _monitor_loop(h):
    global _backlight, _monitorLoopCondition
    x = requestInfo(h)
    if x is None:
        # TODO: error condition
        _monitorLoopCondition = False
        return False
        

    width, height, chunckSize, _backlight = x

    while _monitorLoopCondition:
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
        pass
    return False #disconnect when loop condition is triggered

def errorCb(e):
    print("atmega16u2 monitor error:\n",e)
    return False #disconnect on error

def disconnectCb(e):
    print("atmega16u2 monitor disconnected")
    return True

def sendFigureToMonitor(fig):
    # we want the queue to only hold the most recent frame
    clearQueue(_monitorQueue)
    _monitorQueue.put(fig)


def stopMonitorManager():
    global _monitorLoopCondition
    global _monitorThread
    _monitorLoopCondition = False

# TODO: sometimes blocks, fix this
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
    _monitorThread = Thread(target = lambda : await_connection(const.a16u2monitorVid, const.a16u2monitorPid, _monitor_loop, errorCb, disconnectCb))
    _monitorThread.start()
    print("monitor loop started")
