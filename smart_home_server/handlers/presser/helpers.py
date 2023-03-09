import os
import json
from uuid import uuid4
from threading import Lock
from time import time, sleep

import smart_home_server.constants as const

_rfdevice = None

[
    {'name': 'asdf', 'id': "test", "channels": [
        {"on": 123, "off": 303123},
        {"on": {}, "off": 303123},
        {},
        {"on": 321, "off": 12321}
        ]
     },
    {}
]


_remotes = []
def _loadRemotes():
    global _remotes
    _remotes.clear()
    dir = os.listdir(const.remoteFolder)
    for p in dir:
        path = f'{const.remoteFolder}/{p}'
        print(path)
        with open(path, 'r+') as f:
            remote = json.load(f)
            _remotes.append(remote)
_loadRemotes()
_remoteLock = Lock()


class ChannelDoesNotExist(Exception):
    pass
class RemoteDoesNotExist(Exception):
    pass

def _getRemotePath(id):
    return f'{const.remoteFolder}/{id}.json'

def _getRemotes():
    global _remotes
    return _remotes

def _storeRemote(remote:dict, id: str):
    remote['id'] = id
    with open(_getRemotePath(id), 'w') as f:
        f.write(json.dumps(remote))
    return id

def _addRemote(remote:dict, store:bool = True, newId:bool = True):
    global _remotes
    id = str(uuid4()) if newId else remote['id']
    if store:
        _storeRemote(remote, id)
    _remotes.append(remote)

def _removeRemote(id: str):
    global _remotes

    for i, remote in enumerate(_remotes):
        if remote["id"] != id:
            continue
        _remotes.pop(i)

    path = _getRemotePath(id)
    if os.path.exists(path):
        os.remove(path)


def _overwriteRemote(id:str, remote:dict):
    remote[id] = id
    _removeRemote(id)
    _addRemote(remote, store=True, newId=False)

if const.isRpi():
    def _getCode(timeout = 10, repeats = 3):
        if _rfdevice is None:
            raise Exception("attempted to change button while presser thread is stopped")

        start = time()
        timestamp = None

        currentRepeats = 0
        currentCode = -1
        currentProtocol = -1
        currentPulseLength = 0

        while True:
            if time() > start + timeout:
                return None

            if _rfdevice.rx_code_timestamp != timestamp:
                timestamp = _rfdevice.rx_code_timestamp
                # signal recieved
                if _rfdevice.rx_code != currentCode or _rfdevice.rx_proto != currentProtocol:
                    # new signal
                    currentRepeats = 1
                    currentCode = _rfdevice.rx_code
                    currentProtocol = _rfdevice.rx_proto
                    currentPulseLength = _rfdevice.rx_pulselength
                else:
                    # repeat
                    currentPulseLength += _rfdevice.rx_pulselength
                    currentRepeats+=1

                if currentRepeats > repeats:
                    return {'code': currentCode, 'protocol': currentProtocol, 'pulseLength': round(currentPulseLength / currentRepeats)}

            sleep(0.01)

else:
    def _getCode(timeout = 10, repeats = 3):
        return {'code': 123, 'protocol': 123, 'pulseLength': 123}

def _getRemoteById(id:str, throw:bool = True):
    global _remotes
    for remote in _remotes:
        if remote['id'] != id:
            continue
        return remote
    if throw:
        raise RemoteDoesNotExist(f'No Remote with ID: {id}')
    return None

def _removeChannel(id:str, channel: int):
    remote = _getRemoteById(id)
    assert remote is not None
    if channel >= len(remote['channels']):
        return
    remote['channels'].pop(channel)
    _overwriteRemote(id, remote)

#def _writeChannelValue(id:str, channel: int, value: bool, timeout = 10):
#    remote = _getRemoteById(id)
#    assert remote is not None
#
#    if len(remote['channels']) <= channel:
#        raise ChannelDoesNotExist(f"Max Channel for Remote ID: {id} is {len(remote['channels']-1)} which is < {channel}")
#    if channel < 0:
#        channel = -1
#
#    onOff = "on" if value else "off"
#    code = _getCode(timeout)
#
#    remote['channels'][channel][onOff] = code
#    _overwriteRemote(id, remote)
#
#    return code

def _addChannel(id:str, channel:int, onCode:dict, offCode:dict):
    remote = _getRemoteById(id)
    assert remote is not None

    val = {'on': onCode, 'off': offCode}
    if channel < 0 or len(remote['channels']) <= channel:
        remote['channels'].append(val)
    else:
        remote['channels'].insert(3, val)

    _overwriteRemote(id, remote)

if const.isRpi():
    from rpi_rf import RFDevice

    def _changeChannel(remoteID: str, channel: int, value: bool):
        global _remotes
        global _remoteLock
        if _rfdevice is None:
            raise Exception("attempted to change button while presser thread is stopped")

        with _remoteLock:
            remote = _getRemoteById(remoteID)
            assert remote is not None
            ch = remote[channel]
            #ch = _remotes[remote][channel]
        code = ch.on if value else ch.off

        _rfdevice.tx_code(code, const.txProtocol, const.txPulseLength)
        #print(f'channel={channel}', f'value={value}', flush=True)

    def _initRfDevice():
        global _rfdevice
        _rfdevice = RFDevice(const.txGpio)
        _rfdevice.enable_tx()

    def _destroyRfDevice():
        global _rfdevice
        if _rfdevice is not None:
            _rfdevice.cleanup()

        _rfdevice = None



else:
    def _changeChannel(remote:str, channel: int, value: bool):
        print(f'remote={remote}', f'channel={channel}', f'value={value}', flush=True)

    def _initRfDevice():
        pass

    def _destroyRfDevice():
        pass

