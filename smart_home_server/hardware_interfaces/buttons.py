import smart_home_server.constants as const

if const.isRpi():
    from gpiozero import Button

    def _defaultCallback(pin):
        print("Button Callback Not Set, pin: ", pin)

    _callback = _defaultCallback
    buttons = []

    def _target(button_obj):
        global _callback
        _callback(button_obj.pin.number)

    for pin in const.buttonPins:
        button = Button(pin, pull_up=True)
        button.when_pressed = _target
        buttons.append(button)


    def registerCallback(func):
        global _callback
        _callback = func

else:
    def registerCallback(func):
        print("Register Callback Shim")

