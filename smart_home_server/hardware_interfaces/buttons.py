import smart_home_server.constants as const

if const.isRpi():
    import RPI.GPIO as gpio
    gpio.setmode(gpio.BCM)

    def _defaultCallback(pin):
        print("Button Callback Not Set, pin: ", pin)

    _callback = _defaultCallback

    def _target(pin):
        global _callback
        _callback(pin)

    for pin in const.buttonPins:
        gpio.setup(pin, gpio.IN, pull_up_down=gpio.PUD_UP)
        gpio.add_event_detect(
            pin,
            gpio.FALLING,
            callback = lambda _, p=pin: _target(p),
            debouncetime = 100
        )


    def registerCallback(func):
        global _callback
        _callback = func

    def stopGpio():
        for pin in const.buttonPins:
            gpio.cleanup(pin)

else:
    def registerCallback(func):
        print("Register Callback Shim")

    def stopGpio():
        print("Stop Gpio Shim")

