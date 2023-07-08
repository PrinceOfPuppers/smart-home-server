import os
import json
from uuid import uuid4
from threading import Lock
from time import time, sleep

import smart_home_server.constants as const

_txdevice = None
_rxdevice = None

_remotes = {}

def _loadRemotes():
    global _remotes
    _remotes.clear()
    dir = os.listdir(const.remoteFolder)
    for p in dir:
        path = f'{const.remoteFolder}/{p}'
        with open(path, 'r+') as f:
            remote = json.load(f)
            id = remote['id']
            _remotes[id] = remote
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
    remoteList = [remote for remote in _remotes.values()]
    remoteList.sort(key=lambda x: x['name'])
    return remoteList

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
    _remotes[id] = remote

def _removeRemote(id: str):
    global _remotes

    _remotes.pop(id)

    path = _getRemotePath(id)
    if os.path.exists(path):
        os.remove(path)


def _overwriteRemote(id:str, remote:dict):
    global _remotes

    remote['id'] = id
    _removeRemote(id)
    _addRemote(remote, store=True, newId=False)


def _getRemoteById(id:str, throw:bool = True):
    global _remotes
    try:
        return _remotes[id]
    except KeyError:
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

def _addChannel(id:str, channel:int, onCode:dict, offCode:dict):
    remote = _getRemoteById(id)
    assert remote is not None

    val = {'on': onCode, 'off': offCode}
    if channel < 0 or len(remote['channels']) <= channel:
        remote['channels'].append(val)
    else:
        remote['channels'].insert(channel, val)

    _overwriteRemote(id, remote)

if const.isRpi():
    from rpi_rf import RFDevice

    # timeout = -1 for inf
    def _getCode(timeout, repeats, sleepTimer):
        if _rxdevice is None:
            raise Exception("attempted to change button while presser thread is stopped")

        start = time()
        timestamp = None

        currentRepeats = 0
        currentCode = -1
        currentProtocol = -1
        currentPulseLength = 0

        while True:
            if time() > start + timeout and timeout != -1:
                return None

            if _rxdevice.rx_code_timestamp != timestamp:
                timestamp = _rxdevice.rx_code_timestamp
                # signal recieved
                if _rxdevice.rx_code != currentCode or _rxdevice.rx_proto != currentProtocol:
                    # new signal
                    currentRepeats = 1
                    currentCode = _rxdevice.rx_code
                    currentProtocol = _rxdevice.rx_proto
                    currentPulseLength = _rxdevice.rx_pulselength
                else:
                    # repeat
                    currentPulseLength += _rxdevice.rx_pulselength
                    currentRepeats+=1

                if currentRepeats > repeats:
                    return {'code': currentCode, 'protocol': currentProtocol, 'pulseLength': round(currentPulseLength / currentRepeats)}

            sleep(sleepTimer)

    def _changeChannel(remote: dict, channel: int, value: bool):
        if _txdevice is None:
            raise Exception("attempted to change button while presser thread is stopped")

        with _remoteLock:
            ch = remote['channels'][channel]
            onOff = ch['on'] if value else ch['off']
            code = onOff['code']
            protocol = onOff['protocol']
            pulseLength = onOff['pulseLength']

        for _ in range(const.pressRepeats+1):
            _txdevice.tx_code(code, protocol, pulseLength)

    def _initRfDevices():
        global _rxdevice
        global _txdevice
        _txdevice = RFDevice(const.txGpio)
        _txdevice.enable_tx()

        _rxdevice = RFDevice(const.rxGpio)
        _rxdevice.enable_rx()

    def _destroyRfDevices():
        global _rxdevice
        global _txdevice

        try:
            if _txdevice is not None:
                _txdevice.cleanup()

            if _rxdevice is not None:
                _rxdevice.cleanup()
        except Exception as e:
            print("Error Cleaning Up RF Devices: ", e)

        _rxdevice = None
        _txdevice = None

else:
    def _getCode(timeout, repeats, sleepTimer):
        return {'code': 123, 'protocol': 123, 'pulseLength': 123}

    def _changeChannel(remote:dict, channel: int, value: bool):
        for _ in range(const.pressRepeats+1):
            print(f'remote={remote}', f'channel={channel}', f'value={value}', flush=True)

    def _initRfDevices():
        pass

    def _destroyRfDevices():
        pass

