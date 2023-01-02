import os
import smart_home_server.constants as const

def reboot():
    if const.isRpi():
        os.system('reboot')
    else:
        print('System Rebooted!')
