import os
import smart_home_server.constants as const

from threading import Thread
from time import sleep

def _update():
    # sleep to allow html request to update to return
    sleep(2)
    if const.isRpi():
        os.system(f"git -C {const.modulePath}/.. pull && sudo systemctl restart smart-home-server.service")
    else:
        os.system(f"git -C {const.modulePath}/.. pull")
        print('System Updated!')

def update():
    Thread(target = _update).start()
