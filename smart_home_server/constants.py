from ntpath import dirname
from collections import namedtuple
import os
import re

def createIfNotExists(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


modulePath = dirname(__file__)

pressSpacing = 0.07
pressRepeats = 4

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
            "{clock}{space} {wttrText}\n"
            "T:{temp}/{wttrTemp}{space} H:{humid}/{wttrHumid}"
        )

templatesFolder = f'{modulePath}/templates'
staticFolder = f'{templatesFolder}/static'

TxChannel = namedtuple("Channel", ["on", "off"])

txPulseLength = 171
txProtocol = 1
txGpio = 17

txChannels = [
    #extra channels (below remote)
    TxChannel(on = 5264547, off = 5264547+9),

    #main channels
    TxChannel(on = 5264691, off = 5264700),
    TxChannel(on = 5264835, off = 5264844),
    TxChannel(on = 5265155, off = 5265164),
    TxChannel(on = 5266691, off = 5266700),
    TxChannel(on = 5272835, off = 5272844),

    # extra channels (above remote)
    TxChannel(on = 5282835, off = 5282835+9),
    TxChannel(on = 5292835, off = 5292835+9),
]

# new switches which dont work with old system
txChannels_B = [
    TxChannel(on = 8638540, off = 8638532),
    TxChannel(on = 8638538, off = 8638530),
    TxChannel(on = 8638537, off = 8638529),
    TxChannel(on = 8638541, off = 8638533),
    TxChannel(on = 8638539, off = 8638531),
]


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


_city = "Waterloo+Canada"
fullForecastUrl   = f'http://wttr.in/{_city}'
fullforecastUrlV2 = f'http://v2d.wttr.in/{_city}'
#graphical forcast
forecastUrl       = f'http://wttr.in/{_city}?TQ3n'
# inaccurate current information, used for forcast
wttrApiUrl        = f'http://wttr.in/{_city}?format=j1'
# used for weather image
weatherUrl        = f'http://wttr.in/{_city}?TQ0n'
#used for current condition data
wttrCurrentData   = f'http://wttr.in/{_city}?format=%C\n%t\n%f\n%h\n%p\n%u\n%S\n%s'

#google scraping for dashboard
googleExchangeRateDiv = re.compile(r"<div[^>]+data-exchange-rate\s?=\s?[\"\'](.*?)[\"\'][^>]?>")
fakeUserAgentHeaders = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0"}

lcdI2CAddress = 0x27
lcdLines = 2
lcdWidth = 16

dhtGpio = 22
dhtMinSamplePeriod = 30
dhtMaxRetry = 3
dhtSamples = 2


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
