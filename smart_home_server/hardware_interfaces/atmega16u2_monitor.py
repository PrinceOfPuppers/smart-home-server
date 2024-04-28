#import smart_home_server.constants as const
import hid
#from hid import HIDException
from time import sleep

from typing import Union

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

def sendByte(h:hid.Device,b:bytes):
    h.write(b + b'\n')

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
        if len(data) == 0:
            print("read byte timeout")
        else:
            print("read byte invalid len", len(data))
        # TODO: error condition
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
        print("recieved err byte")
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
        print(f"expected {c} got {x}")
        return False
    return True



def sendFrame(h:hid.Device, b:bytearray, chunkByteSize:int):
    # TODO: add timeout to all reads
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
            print(len(x))
            exit(1)
        h.write(x)

        res = readByte(h)
        if res == None:
            return

        if res != ackByte:
            break

    # TODO: report as error condition
    while res == ackByte:
        print("filling with black")
        # fill rest with black
        x = bytes(b[0xFF])*chunkByteSize
        h.write(x)
        res = readByte(h)

    # TODO: report as error condition
    if res != lastByte:
        print("non-L return: ", res)
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

    # TODO: sanity check values, report error condition

    sendByte(h, ackByte)
    print(f"{width=}, {height=}, {chunkSize=}, {backlight=}")
    return width, height, chunkSize, backlight
