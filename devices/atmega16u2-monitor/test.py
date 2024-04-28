from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import smart_home_server.constants as const
from smart_home_server.hardware_interfaces.atmega16u2_monitor import sendFrame, requestInfo, rgb_to_16_bit
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
