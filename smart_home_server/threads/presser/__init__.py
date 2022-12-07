from time import sleep
from queue import Queue, Empty
from threading import Thread

import smart_home_server.constants as const
from smart_home_server.helpers import clearQueue

_pressQueue = Queue()
_presserLoopCondition  = False
_presserThread = None

_rfdevice = None

if const.isRpi():
    from rpi_rf import RFDevice
    def _changeChannel(channel: int, value: bool):
        if _rfdevice is None:
            raise Exception("attempted to change button while presser thread is stopped")

        ch = const.txChannels[channel]
        code = ch.on if value else ch.off

        _rfdevice.tx_code(code, const.txProtocol, const.txPulseLength)
        #print(f'channel={channel}', f'value={value}', flush=True)
else:
    def _changeChannel(channel: int, value: bool):
        print(f'channel={channel}', f'value={value}', flush=True)

def _presserLoop():
    global _pressQueue
    global _presserLoopCondition

    while _presserLoopCondition:
        try:
            try:
                press = _pressQueue.get(block=True, timeout = const.threadPollingPeriod)
            except Empty:
                continue
            for _ in range(const.pressRepeats+1):
                _changeChannel(press['channel'], press['value'])
                sleep(const.pressSpacing)

        except Exception as e:
            print(f"Presser Exception: \n{repr(e)}", flush=True)
            continue

def presserAppend(press):
    global _pressQueue
    _pressQueue.put(press)

def stopPresser():
    global _presserLoopCondition

    if const.isRpi():
        global _rfdevice
        if _rfdevice is not None:
            _rfdevice.cleanup()

    _rfdevice = None
    _presserLoopCondition = False

def joinPresser():
    global _presserLoopCondition
    global _presserThread
    if _presserThread is not None and _presserThread.is_alive():
        _presserLoopCondition = False
        _presserThread.join()
    else:
        _presserLoopCondition = False

def startPresser():
    global _pressQueue
    global _presserLoopCondition
    global _presserThread
    global _rfdevice

    if const.isRpi():
        _rfdevice = RFDevice(const.txGpio)
        _rfdevice.enable_tx()

    if _presserLoopCondition:
        raise Exception("Presser Already Running")

    joinPresser() # incase its still stopping

    clearQueue(_pressQueue)
    _presserLoopCondition = True
    _presserThread = Thread(target=_presserLoop)
    _presserThread.start()
    print("presser started")
