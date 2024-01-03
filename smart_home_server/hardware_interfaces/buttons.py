from time import time

import smart_home_server.constants as const

class ButtonInvalidPin(Exception):
    pass

if const.isRpi():
    import pigpio

    def _defaultCallback(pin):
        print("Button Callback Not Set, pin: ", pin)

    _callback = _defaultCallback
    _lastCalled = {}

    def _target(pin, _, __):
        global _callback
        global _lastCalled

        t = time()
        if t < _lastCalled[pin] + const.buttonDebounce:
            return

        _lastCalled[pin] = t
        _callback(pin)

    _pi = pigpio.pi()
    for pin in const.buttonPins:
        _lastCalled[pin] = 0
        _pi.set_pull_up_down(pin, pigpio.PUD_UP)
        _pi.callback( pin, pigpio.FALLING_EDGE, _target )


    def registerCallback(func):
        global _callback
        _callback = func

else:
    def registerCallback(func):
        print("Register Callback Shim")

