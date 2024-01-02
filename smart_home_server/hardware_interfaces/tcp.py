import socket
from typing import Callable
import struct
from threading import Thread

from smart_home_server.errors import currentErrors
import smart_home_server.constants as const

def disconnectSocket(c:socket.socket):
    try:
        c.shutdown(socket.SHUT_RDWR)
    except:
        pass

    try:
        c.close()
    except:
        pass

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


def is_socket_closed(sock: socket.socket) -> bool:
    try:
        # this will try to read bytes without blocking and also without removing them from buffer (peek only)
        data = sock.recv(16, socket.MSG_DONTWAIT | socket.MSG_PEEK)
        if len(data) == 0:
            return True
    except BlockingIOError:
        return False  # socket is open and reading from it would block
    except ConnectionResetError:
        return True  # socket was closed for some other reason
    except Exception as e:
        print("unexpected exception when checking if a socket is closed")
        return False
    return False


# packets are null terminated
def tcpSendPacket(c:socket.socket, s:str):
    print("is closed: ", is_socket_closed(c))
    try:
        print("sending: ", s)
        print(c.send(s.encode()))
        print(c.send(b'\x00'))
        print("sent!")
    except Exception as e:
        print(e)
        return False
    return True


def tcpListener(port:int, onConnect:Callable, continueCb:Callable, **kwargs):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.bind(('', port))
    s.listen()
    s.settimeout(1)
    print("TCP Listener Started on Port: ", port)
    while continueCb():
        try:
            c, addr = s.accept()
            # keep alive settings
            #c.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            #c.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 1)
            #c.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 3)
            #c.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)

            # override default timeout settings
            c.setsockopt(socket.IPPROTO_TCP, socket.TCP_USER_TIMEOUT, const.tcpTimeout)
        except socket.timeout:
            continue

        Thread(target=onConnect, args=(c,addr), kwargs=kwargs).start()
    disconnectSocket(s)


