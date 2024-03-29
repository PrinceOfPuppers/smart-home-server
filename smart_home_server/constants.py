from ntpath import dirname
from collections import namedtuple
import os
import re

TxChannel = namedtuple("Channel", ["on", "off"])

colors = {
    "darkGrey": "#1e1f1c",
    "grey": "#272822",
    "lightGrey": "#75715e",
    "white": "#f8f8f2",
    "purple": "#B267E6",
    "red": "#F92672",
    "blue": "#66D9EF",
    "green": "#A6E22E",
    "yellow": "#E6DB74",
    "orange": "#FD971F"
}

def createIfNotExists(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


modulePath = dirname(__file__)

#pressSpacing = 0.07
pressRepeats = 4

templatesFolder = f'{modulePath}/templates'
staticFolder = f'{templatesFolder}/static'


storageFolder = f'{modulePath}/storage'
createIfNotExists(storageFolder)
schedulerJobFolder = f'{storageFolder}/jobs'
createIfNotExists(schedulerJobFolder)

triggeredJobFolder = f'{storageFolder}/triggers'
createIfNotExists(triggeredJobFolder)

lcdTextFile = f'{storageFolder}/lcd.txt'
if not os.path.exists(lcdTextFile):
    with open(lcdTextFile,"w") as f:
        f.write(
            "{clock}{space} P:{wttrTotalPercip}mm\n"
            "T:{temp}/{wttrTemp}{space} H:{humid}/{wttrHumid}\n"
            "\n"
            ""
        )

noteFolder = f'{storageFolder}/notes'
createIfNotExists(noteFolder)

macroFolder = f'{storageFolder}/macros'
createIfNotExists(macroFolder)

remoteFolder = f'{storageFolder}/remotes'
createIfNotExists(remoteFolder)

lcdsFolder = f'{storageFolder}/lcds'
createIfNotExists(lcdsFolder)

graphsFolder = f'{storageFolder}/graphs'
createIfNotExists(graphsFolder)

# defaultRemoteFileA = f'{storageFolder}/remotes/A'
# if not os.path.exists(defaultRemoteFileA):
#     with open(defaultRemoteFileA,"w") as f:
#         f.write(
#             "A\n"
#             #extra channels (below remote)
#             f"{5264547}, {5264547+9}\n"
# 
#             #main channels
#             f"{5264691}, {5264700}\n"
#             f"{5264835}, {5264844}\n"
#             f"{5265155}, {5265164}\n"
#             f"{5266691}, {5266700}\n"
#             f"{5272835}, {5272844}\n"
# 
#             # extra channels (above remote)
#             f"{5282835}, {5282835+9}\n"
#             f"{5292835}, {5292835+9}\n"
#         )
# 
# defaultRemoteFileB = f'{storageFolder}/remotes/B'
# if not os.path.exists(defaultRemoteFileB):
#     with open(defaultRemoteFileB,"w") as f:
#         f.write(
#             "B\n"
#             f"{8638540}, {8638532}\n"
#             f"{8638538}, {8638530}\n"
#             f"{8638537}, {8638529}\n"
#             f"{8638541}, {8638533}\n"
#             f"{8638539}, {8638531}\n"
#         )

#remotes = {}
# parse remotes
# def loadRemotes():
#     global remotes
#     dir = os.listdir(remoteFolder)
#     for p in dir:
#         path = f'{remoteFolder}/{p}'
#         f = open(path, 'r+')
#         try:
#             lines = f.readlines()
#             if len(lines) < 2:
#                 f.close()
#                 os.remove(path)
#                 continue
#             name = lines[0].strip()
#             buttons = []
#             for line in lines[1:]:
#                 try:
#                     on, off = line.split(',')
#                     on  = int(on.strip())
#                     off = int(off.strip())
#                 except Exception as e:
#                     print(e)
#                     continue
#                 buttons.append(TxChannel(on=on, off=off))
#             if len(buttons) < 1:
#                 f.close()
#                 os.remove(path)
#                 continue
#             remotes[name] = buttons
#         finally:
#             f.close()
#loadRemotes()


txGpio = 17
rxGpio = 25

#seconds
threadPollingPeriod = 1


_isRpi = None
def isRpi():
    global _isRpi
    if _isRpi is not None:
        return _isRpi

    _isRpi = False
    path = '/sys/firmware/devicetree/base/model'
    if os.path.exists(path):
        with open(path, 'r') as m:
            if 'raspberry pi' in m.read().lower():
                _isRpi = True
    return _isRpi

requestTimeout = 5
_city = "43.4652699,-80.5222961" # Waterloo Canada
fullForecastUrl   = f'http://wttr.in/{_city}'
fullforecastUrlV2 = f'http://v2d.wttr.in/{_city}'
#graphical forcast
forecastUrl       = f'http://wttr.in/{_city}?TQ3n'
# inaccurate current information, used for forcast
wttrApiUrl        = f'http://wttr.in/{_city}?format=j1'
# used for weather image
weatherUrl        = f'http://wttr.in/{_city}?TQ0n'
#used for current condition data
#wttrCurrentData   = f'http://wttr.in/{_city}?format=%C\n%t\n%f\n%h\n%p\n%u\n%S\n%s'
wttrCurrentData   = f'http://wttr.in/{_city}?format=%C\n%t\n%f\n%h\n%p\n%u\n'

#google scraping for dashboard
googleExchangeRateDiv = re.compile(r"<div[^>]+data-exchange-rate\s?=\s?[\"\'](.*?)[\"\'][^>]?>")
fakeUserAgentHeaders = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0"}

lcdI2CAddress = 0x27
maxLcdLines = 4  # max lines supported for all lcds
localLcdLines = 4
lcdWidth = 20
lcdDefaultName = "New Lcd"

dhtGpio = 22
dhtGpioPwr = 18
dhtMinSamplePeriod = 30
dhtMaxRetry = 3
dhtSamples = 2


# in seconds
rfMacroDebounceTime = 3
# time after rf is added to macro to when macros can be triggered by rf again
rfMacroAddDebounceTime = 1
pulseLenthTolerance = 10

# max hours graphs can display
graphMaxHours = 128

# for indoor climate measuring, if neither dht or bme, indoorWeatherServer will be used
useDht22 = False
useBME = False
assert not (useDht22 and useBME)


# server buttons
buttonPins = [23,24]
# in seconds, applies to all button interfaces
buttonDebounce = 0.8
buttonMacroAddDebounceTime = 1


#udp
udpTimeout = 2
outdoorWeatherServerIp = "192.168.2.151"
indoorWeatherServerIp  = "192.168.2.152"
printChamberWeatherServerIp  = "192.168.2.153"
officeChamberWeatherServerIp  = "192.168.2.159"
weatherServerPort = 6831
airQualityServerIP = "192.168.2.160"
airQualityServerPort = 6833


#tcp
tcpTimeout = 20
lcdListenerPort = 6832
lcdCmdEscapeChar = "\x1b"

# when should remote lcds attempt reconnect
lcdDashReconnectTime = 20*60;


WWO_CODE = {
    "113": "Sunny",
    "116": "PartlyCloudy",
    "119": "Cloudy",
    "122": "VeryCloudy",
    "143": "Fog",
    "176": "LightShowers",
    "179": "LightSleetShowers",
    "182": "LightSleet",
    "185": "LightSleet",
    "200": "ThunderyShowers",
    "227": "LightSnow",
    "230": "HeavySnow",
    "248": "Fog",
    "260": "Fog",
    "263": "LightShowers",
    "266": "LightRain",
    "281": "LightSleet",
    "284": "LightSleet",
    "293": "LightRain",
    "296": "LightRain",
    "299": "HeavyShowers",
    "302": "HeavyRain",
    "305": "HeavyShowers",
    "308": "HeavyRain",
    "311": "LightSleet",
    "314": "LightSleet",
    "317": "LightSleet",
    "320": "LightSnow",
    "323": "LightSnowShowers",
    "326": "LightSnowShowers",
    "329": "HeavySnow",
    "332": "HeavySnow",
    "335": "HeavySnowShowers",
    "338": "HeavySnow",
    "350": "LightSleet",
    "353": "LightShowers",
    "356": "HeavyShowers",
    "359": "HeavyRain",
    "362": "LightSleetShowers",
    "365": "LightSleetShowers",
    "368": "LightSnowShowers",
    "371": "HeavySnowShowers",
    "374": "LightSleetShowers",
    "377": "LightSleet",
    "386": "ThunderyShowers",
    "389": "ThunderyHeavyRain",
    "392": "ThunderySnowShowers",
    "395": "HeavySnowShowers",
}

WEATHER_SYMBOL = {
    "Unknown":             ("✨",2),
    "Cloudy":              ("☁️" ,2),
    "Fog":                 ("🌫",2),
    "HeavyRain":           ("🌧",2),
    "HeavyShowers":        ("🌧",2),
    "HeavySnow":           ("❄️" ,2),
    "HeavySnowShowers":    ("❄️" ,2),
    "LightRain":           ("🌦",2),
    "LightShowers":        ("🌦",2),
    "LightSleet":          ("🌧",2),
    "LightSleetShowers":   ("🌧",2),
    "LightSnow":           ("🌨",2),
    "LightSnowShowers":    ("🌨",2),
    "PartlyCloudy":        ("⛅️",2),
    "Sunny":               ("☀️" ,2),
    "ThunderyHeavyRain":   ("🌩",2),
    "ThunderyShowers":     ("⛈" ,2),
    "ThunderySnowShowers": ("⛈" ,2),
    "VeryCloudy":          ("☁️" ,2),
}

months = ['Jan','Feb','Mar','Apr','May','June','July','Aug','Sept','Oct','Nov','Dec']
