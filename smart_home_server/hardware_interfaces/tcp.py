import socket
from typing import Callable
from threading import Thread

from smart_home_server.errors import currentErrors
import smart_home_server.constants as const

def tcpErr(err):
    if err:
        currentErrors['TCP_Err'] += 1
    else:
        currentErrors['TCP_Err'] = 0

# packets are null terminated
def tcpRecievePacket(c:socket.socket):
    x = bytes()
    while True:
        y = c.recv(1)
        if y == b'\x00':
            break
        x += y

    return x.decode()

# packets are null terminated
def tcpSendPacket(c:socket.socket, s:str):
    try:
        c.send(s.encode())
        c.send(b'\x00')
    except Exception as e:
        print(e)
        return False
    return True


def tcpListener(port:int, onConnect:Callable, continueCb:Callable, **kwargs):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', port))
    s.listen()
    print("TCP Listener Started on Port: ", port)
    while continueCb():
        c, addr = s.accept()
        Thread(target=onConnect, args=(c,addr), kwargs=kwargs).start()
    s.close()


