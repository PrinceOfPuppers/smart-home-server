from ntpath import dirname
from collections import namedtuple
import os

modulePath = dirname(__file__)

pressSpacing = 10
pressRepeats = 0
maxChannels = 5

schedulerJobFolder = f'{modulePath}/jobs'
templateFolder = f'{modulePath}/templates'

TxChannel = namedtuple("Channel", ["on", "off"])

txPulseLength = 171
txProtocol = 1
txGpio = 17

txChannels = [
    #extra channels (below remote)
    TxChannel(on = 5264547, off = 5264547+9),

    #main channels
    TxChannel(on = 5264691, off = 5264700),
    TxChannel(on = 5264835, off = 5264844),
    TxChannel(on = 5265155, off = 5265164),
    TxChannel(on = 5266691, off = 5266700),
    TxChannel(on = 5272835, off = 5272844),

    # extra channels (above remote)
    TxChannel(on = 5282835, off = 5282835+9),
    TxChannel(on = 5292835, off = 5292835+9),
]

#seconds
pollingPeriod = 1

_isRpi = None
def isRpi():
    global _isRpi
    if _isRpi is not None:
        return _isRpi

    _isRpi = False
    path = '/sys/firmware/devicetree/base/model'
    if os.path.exists(path):
        with open(path, 'r') as m:
            if 'raspberry pi' in m.read().lower(): 
                _isRpi = True
    return _isRpi
    
