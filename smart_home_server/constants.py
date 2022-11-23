from ntpath import dirname
from collections import namedtuple
import os
import re

def createIfNotExists(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

modulePath = dirname(__file__)

pressSpacing = 0.1
pressRepeats = 2

storageFolder = f'{modulePath}/storage'
createIfNotExists(storageFolder)
schedulerJobFolder = f'{storageFolder}/jobs'
createIfNotExists(schedulerJobFolder)

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
forecastUrl       = f'http://wttr.in/{_city}?TQ3n'
wttrApiUrl        = f'http://wttr.in/{_city}?format=j1'
weatherUrl        = f'http://wttr.in/{_city}?TQ0n'

# colors are blue, green, red, purple, yellow, orange, white, gray
dashboardElements = [
    {
        'name': 'USD → CAD',
        'enabled':True,
        'color': 'green',
        'url': 'api/dashboard/forex?from=usd&to=cad',
        'pollingPeriod': 5*60,
    },
    {
        'name': 'Weather',
        'enabled':False,
        'color': 'blue',
        'url': f'api/dashboard/weather',
        'pollingPeriod': 10*60,
    },
    {
        'name': 'Forecast',
        'enabled': True,
        'color': 'blue',
        'url': f'api/dashboard/forecast',
        'pollingPeriod': 10*60,
    },
    {
        'name': 'Large-Forecast',
        'enabled': False,
        'color': 'blue',
        'url': f'api/dashboard/large-forecast',
        'pollingPeriod': 10*60,
    },
]

#google scraping for dashboard
googleExchangeRateDiv = re.compile(r"<div[^>]+data-exchange-rate\s?=\s?[\"\'](.*?)[\"\'][^>]?>")
fakeUserAgentHeaders = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0"}

