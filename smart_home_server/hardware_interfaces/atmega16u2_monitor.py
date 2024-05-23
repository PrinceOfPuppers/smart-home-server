import hid
from pyudev import Context, Monitor
from time import sleep
from threading import Thread
from functools import partial

import smart_home_server.constants as const
from typing import Union, Callable

readTimeout = 100

# from device
lastByte = b'L'
errByte = b'E'


# to device
infoByte = b'I'
startByte = b'S'
backlightByte = b'B'

# both
ackByte = b'A'

sendAttempts = 3

def sendBytes(h:hid.Device,b:bytes):
    for i in range(0, sendAttempts):
        try:
            h.write(b)
            return
        except:
            sleep(0.01)
            continue
    raise hid.HIDException("Max Send Attempts Reached")

def sendByte(h:hid.Device,b:bytes):
    sendBytes(h, b + b'\n')


rlut = [(i >> (8-5)) << (16 - 5) for i in range(0,256)]
glut = [(i >> (8-6)) << (16 - 11) for i in range(0,256)]
blut = [i >> (8-5) for i in range(0,256)]

def rgb_to_16_bit(rgb_buffer):
    #b = bytearray()
    #iterate over sets of 3 bytes
    numPixels = len(rgb_buffer)//3

    b = bytearray(2*numPixels)

    for i in range(numPixels):
        # 16 bit value
        x = rlut[rgb_buffer[3*i]] + glut[rgb_buffer[3*i+1]] + blut[rgb_buffer[3*i+2]]

        # little endiean
        b1 = (x%256)
        b2 = (x//256)


        #split into 2 bytes (and filter out nullbytes)
        b[2*i] = b1 if b1 != 0 else 1
        b[2*i+1] = b2 if b2 != 0 else 8

    return b

def readBytes(h:hid.Device, n:int) -> Union[bytes,None]:
    data = h.read(n, readTimeout)
    if len(data) != n:
        sendByte(h, errByte)
        sleep(0.001) # wait for 1 ms for write to stop
        # clear buffer
        while(len(h.read(1,0)) != 0):
            pass
        return None
    return data

def readByte(h:hid.Device):
    b = readBytes(h,1)
    if b == errByte:
        # TODO: purge buffer?
        sleep(0.002) # wait for 2 ms to allow device to purge buffer
        return None
    return b



# returns true for expected byte, false otherwise
def expectByte(h:hid.Device, c):
    x = readByte(h)
    if x == None:
        return False
    if x != c:
        return False
    return True

def sendFrame(h:hid.Device, b:bytearray, chunkByteSize:int):
    sendByte(h, startByte)
    if not expectByte(h, ackByte):
        return


    assert len(b) % chunkByteSize == 0
    chunks = len(b) / chunkByteSize
    chunks = int(chunks)

    res = b"-"
    for i in range(chunks):
        start = i*chunkByteSize
        x = bytes(b[start:start+chunkByteSize])
        if len(x) != chunkByteSize:
            # TODO: report error
            pass
        sendBytes(h,x)

        res = readByte(h)
        if res == None:
            return

        if res != ackByte:
            break

    while res == ackByte:
        #print("filling with black")
        # fill rest with black
        x = bytes(b[0xFF])*chunkByteSize
        sendBytes(h, x)
        res = readByte(h)

    # TODO: report as error condition
    if res != lastByte:
        #print("non-L return: ", res)
        pass



def requestInfo(h:hid.Device):
    sendByte(h, infoByte)
    b = readBytes(h, 8)
    if b == None:
        return None

    width = int.from_bytes(b[0:2], byteorder="little")
    height = int.from_bytes(b[2:4], byteorder = "little")
    chunkSize = int.from_bytes(b[4:6], byteorder = "little")
    backlight = int.from_bytes(b[6:8], byteorder = "little")

    sendByte(h, ackByte)
    #print(f"{width=}, {height=}, {chunkSize=}, {backlight=}")
    return width, height, chunkSize, backlight



def _thread_target(sequence: Callable[[], int], callback:Callable[[hid.Device,Callable[[],int]],None], deviceVid:int, devicePid:int, reconn:bool = True):
    seq = sequence()
    while sequence() == seq:
        try:
            with hid.Device(deviceVid, devicePid) as h:
                callback(h, sequence)
        except:
            if reconn:
                sleep(3) # in case of exception, wait before attempting reconnect (anti spam)
                continue
            break


# will attempt reconnect on crash
def await_connection(loopCondition: Callable[[], bool], callback:Callable[[hid.Device,Callable[[],int]],None], deviceVid:int, devicePid:int):
    ctx = Context()
    ctx.list_devices(subsystem='usb')

    monitor = Monitor.from_netlink(ctx)
    monitor.filter_by(subsystem='usb')

    seq = 0
    t = Thread(target = lambda: _thread_target(lambda: seq, callback, deviceVid, devicePid, reconn=False)) # attempt inital connection
    t.start()

    while loopCondition():
        for device in iter(partial(monitor.poll, const.threadPollingPeriod), None):
            if device == None:
                continue

            if 'PRODUCT' in device and 'BUSNUM' in device:
                prod = device.get("PRODUCT")
                if not isinstance(prod, str):
                    continue
                x = prod.split("/")
                if len(x) < 2:
                    continue
                try:
                    vid = int(x[0], 16)
                    pid = int(x[1], 16)
                except:
                    continue

                if vid != deviceVid or pid != devicePid:
                    continue

                if device.action == "bind":
                    t = Thread(target = lambda: _thread_target(lambda: seq, callback, deviceVid, devicePid))
                    t.start()
                elif device.action == "unbind":
                    seq += 1
                    try:
                        t.join()
                    except:
                        pass

    seq = -1
    try:
        t.join()
    except:
        pass

