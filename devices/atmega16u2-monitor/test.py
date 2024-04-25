from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import hid
from time import sleep

def test():
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


    SMALL_SIZE = 5
    MEDIUM_SIZE = 6
    BIGGER_SIZE = 7

    plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
    plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
    plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
    plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

    #plt.rcParams['figure.figsize'] = [1, 4]

    xs = [0,1,2,3,4,5,6,7,8,9]
    ys = [3,1,2,5,6,7,1,2,3,4]
    px = 1/plt.rcParams['figure.dpi']
    fig = Figure(figsize=(160*px,128*px))
    #fig.set_figheight()
    #fig.set_figwidth()
    blue = "#66D9EF"
    axis = fig.add_subplot(1, 1, 1)
    axis.plot(xs, ys, color=blue)
    axis.set_xlabel("test")
    axis.set_title("test2")


    #FigureCanvas(fig).print_raw("./test.raw")
    c = FigureCanvas(fig)
    c.draw()
    b = c.tostring_rgb()
    return b

rlut = [(i >> (8-5)) << (16 - 5) for i in range(0,255)]
glut = [(i >> (8-6)) << (16 - 11) for i in range(0,255)]
blut = [i >> (8-5) for i in range(0,255)]

def rgb_to_16_bit(rgb_buffer):
    #b = bytearray()
    #iterate over sets of 3 bytes
    numPixels = len(rgb_buffer)//3

    b = bytearray(2*numPixels)

    for i in range(numPixels):
        # 16 bit value
        x = rlut[rgb_buffer[3*i]] + glut[rgb_buffer[3*i+1]] + blut[rgb_buffer[3*i+2]]
        b1 = (x%256)
        b2 = (x//256)


        #split into 2 bytes (and filter out nullbytes)
        b[2*i] = b1 if b1 != 0 else 1
        b[2*i+1] = b2 if b2 != 0 else 8

        #b.append(x//256)
        #b.append(x%256)

    return b

def sendFrame(h:hid.Device, b:bytearray, chunkByteSize:int):
    assert len(b) % chunkByteSize == 0
    chunks = len(b) / chunkByteSize
    chunks = int(chunks)


    for i in range(chunks):
        start = i*chunkByteSize
        x = bytes(b[start:start+chunkByteSize])
        if len(x) != chunkByteSize:
            print(len(x))
            exit(1)
        written = h.write(x)
        #print(x.hex(" "), written)
        #sleep(0.01)
        #wait for ack
        h.read(1)
        #sleep(0.1)





def hidTest():

    # ATTRS{idVendor}=="2341", ATTRS{idProduct}=="484c", MODE="660", GROUP="plugdev", TAG+="uaccess"

    vid = 0x2341	# Change it for your device
    pid = 0x484C	# Change it for your device

    #vid = 0x046d	# Change it for your device
    #pid = 0xc332    # Change it for your device

    #vid = 0x045e
    #pid = 0x082c

    with hid.Device(vid, pid) as h:
        h.serial
        print(f'Device manufacturer: {h.manufacturer}')
        print(f'Product: {h.product}')
        print(f'Serial Number: {h.serial}')

        #h.write("aaa\n".encode('utf8'))
        #h.write("aaa\n".encode('utf8'))
        #x = h.read(6)
        #print(x.decode("utf8"))

        b = rgb_to_16_bit(test())
        sendFrame(h, b, 40)
        # sendFrame(h, b, 2)

        #h.write(imgbytes)


hidTest()
