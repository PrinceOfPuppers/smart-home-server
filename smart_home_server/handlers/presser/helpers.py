import smart_home_server.constants as const

_rfdevice = None

if const.isRpi():
    from rpi_rf import RFDevice

    def _changeChannel(remote: str, channel: int, value: bool):
        if _rfdevice is None:
            raise Exception("attempted to change button while presser thread is stopped")

        ch = const.remotes[remote][channel]
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

