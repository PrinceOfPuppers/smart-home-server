from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import smart_home_server.constants as const
from matplotlib.axes import Axes
import hid
from hid import HIDException
from time import sleep

from typing import Union

readTimeout = 100

def test(color, width, height):
    from matplotlib.figure import Figure
    import matplotlib.pyplot as plt
    import smart_home_server.constants as const
    import matplotlib as mpl

    textColor = const.colors["white"]
    mpl.rcParams['text.color'] = textColor
    mpl.rcParams['axes.labelcolor'] = textColor
    mpl.rcParams['xtick.color'] = textColor
    mpl.rcParams['ytick.color'] = textColor
    mpl.rcParams['figure.facecolor'] = const.colors["grey"]
    mpl.rcParams['axes.facecolor'] = const.colors["darkGrey"]


    SMALL_SIZE = 6
    MEDIUM_SIZE = 7
    BIGGER_SIZE = 8

    #plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
    #plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
    #plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
    #plt.rc('axes', titlesize=BIGGER_SIZE)    # fontsize of the x and y labels
    #plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    #plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    #plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
    #plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

    #plt.rcParams['figure.figsize'] = [1, 4]

    xs = [0,1,2,3,4,5,6,7,8,9]
    ys = [300,100,200,500,600,700,100,200,300,400]
    px = 1/plt.rcParams['figure.dpi']
    fig = Figure(figsize=(width*px,height*px))
    #fig.tight_layout(pad=10, h_pad=0)
    fig.subplots_adjust(right=0.95)
    #blue = "#66D9EF"
    axis:Axes = fig.add_subplot(1, 1, 1)
    axis.plot(xs, ys, color=color)
    axis.tick_params(labelsize=SMALL_SIZE)
    #axis.set_xlabel("test")
    axis.set_title("test2 over Hours", pad=3, size=BIGGER_SIZE)
    axis.tick_params(length=0, color=const.colors["black"], pad=2)


    #FigureCanvas(fig).print_raw("./test.raw")
    c = FigureCanvas(fig)
    c.draw()
    b = c.tostring_rgb()
    return b





# from device
lastByte = b'L'
errByte = b'E'


# to device
infoByte = b'I'
startByte = b'S'
backlightByte = b'B'

# both
ackByte = b'A'

def sendByte(h,b):
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

def readBytes(h, n) -> Union[bytes,None]:
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

def readByte(h):
    b = readBytes(h,1)
    if b == errByte:
        print("recieved err byte")
        # TODO: purge buffer?
        sleep(0.002) # wait for 2 ms to allow device to purge buffer
        return None
    return b



# returns true for expected byte, false otherwise
def expectByte(h, c):
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



def hidTest(vid, pid):
    #vid = 0x2341
    #pid = 0x484C

    with hid.Device(vid, pid) as h:
        print(f'Device manufacturer: {h.manufacturer}')
        print(f'Product: {h.product}')
        print(f'Serial Number: {h.serial}')


        width, height, chunckSize,backlight = requestInfo(h)

        i = 0
        colors = [c for c in const.colors.values()]
        while True:
            b = rgb_to_16_bit(test(colors[i], width, height))
            sendFrame(h, b, chunckSize)
            sleep(5)
            i+=1
            i%=len(colors)


def await_connection():
    # try to connect at startup
    try:
        hidTest(const.a16u2monitorVid, const.a16u2monitorPid)
    except HIDException:
        pass


    from pyudev import Context, Monitor

    ctx = Context()
    ctx.list_devices(subsystem='usb')

    monitor = Monitor.from_netlink(ctx)
    monitor.filter_by(subsystem='usb')


    while True:
        for device in iter(monitor.poll, None):
            if device == None:
                continue

            if device.action == 'bind' and 'PRODUCT' in device and 'BUSNUM' in device:
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

                if vid != const.a16u2monitorVid  or pid != const.a16u2monitorPid:
                    continue

                try:
                    hidTest(vid, pid) # must be blocking to prevent spam connecting
                except HIDException:
                    print("disconnect")
                    continue





await_connection()
