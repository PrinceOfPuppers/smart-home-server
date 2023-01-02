import os
import smart_home_server.constants as const

def reboot():
    if const.isRpi():
        os.system('sudo systemctl start reboot.target')
    else:
        print('System Rebooted!')
