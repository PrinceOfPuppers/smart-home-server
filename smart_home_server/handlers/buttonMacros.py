from queue import Queue,Empty
from typing import Union

from smart_home_server.handlers.macros import getMacroWithButton, getMacroWithButton
from smart_home_server.hardware_interfaces.buttons import registerCallback
from smart_home_server.handlers import runMacro

from smart_home_server.helpers import clearQueue
import smart_home_server.constants as const

_addButtonModeEnabled = False
_addButtonQueue = Queue()

def buttonPressed(pin):
    global _addButtonModeEnabled
    global _addButtonQueue

    if _addButtonModeEnabled:
        _addButtonQueue.put(pin)
        return

    macro = getMacroWithButton(pin)
    if macro is None:
        return

    runMacro(macro['id'])


# start macroButton Presser
registerCallback(buttonPressed)


if const.isRpi():
    def getButtonPressed(timeout = 3) -> Union[None, int]:
        global _addButtonModeEnabled
        global _addButtonQueue

        clearQueue(_addButtonQueue)
        _addButtonModeEnabled = True
        try:
            pin = _addButtonQueue.get(timeout=timeout)
        except Empty:
            return None
        _addButtonModeEnabled = False
        clearQueue(_addButtonQueue)
        return pin

else:
    def getButtonPressed(timeout = 3) -> Union[None, int]:
        input("Web Thread: Hit Enter to Send Psudo Button pin (timeout ignored)")
        return 3
