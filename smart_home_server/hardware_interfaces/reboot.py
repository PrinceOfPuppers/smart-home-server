import os
import smart_home_server.constants as const

from threading import Thread
from time import sleep

def _reboot():
    # sleep to allow html request to reboot to return
    sleep(2)
    if const.isRpi():
        os.system('sudo systemctl start reboot.target')
    else:
        print('System Rebooted!')

def reboot():
    Thread(target = _reboot).start()
