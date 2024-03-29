import requests
from datetime import datetime
from typing import Union

from smart_home_server.hardware_interfaces.dht22 import getDHT
from smart_home_server.hardware_interfaces.bme280 import getBME
from smart_home_server.hardware_interfaces.udp import getWeatherServerData, getAirQualityServerData
from smart_home_server.helpers import padChar
import smart_home_server.constants as const

from smart_home_server.data_sources.caching import cached
from smart_home_server import __version__

from smart_home_server.errors import getErrorStrAndBool
from smart_home_server.handlers.logs import jobLog, rfLog

# return format is
#example = {
#    'str': f'Temprature: 123 \nHumidity: 123',
#    'data': {
#        "temp": 123,
#        "humid": 123
#    },
#}

def getErrors():
    s, anyErr = getErrorStrAndBool()
    res = {
        'str': s,
        'data': {'anyErrors' : anyErr},
    }
    return res

def getForexLocal(src,dest, decimal=3):
    try:
        r = requests.get(f'https://www.google.com/search?q={src}+to+{dest}', headers=const.fakeUserAgentHeaders, timeout=const.requestTimeout)
    except:
        return None
    if not r.ok:
        return None

    x = const.googleExchangeRateDiv.search(r.text)
    if not x:
        return None

    rate = str(round(float(x.group(1)),decimal))
    res = {
        'str': str(rate),
        'data': {
            'src': src,
            'dest': dest,
            'rate': rate,
        },
    }
    return res

def getForecastLocal():
    # prevent spamming wttrin while testing
    if not const.isRpi():
        return None

    r = requests.get(const.wttrApiUrl, timeout=const.requestTimeout)

    # calculate marked bar (denotes the current time)
    n = datetime.now()
    currentDay = n.date().day
    currentHour:float = float(n.hour) + float(n.minute) / 60
    timeStep = 3/4

    x = list("────────────────────────────────")

    index = round(currentHour/timeStep)
    index = index if index < len(x) else len(x) - 1

    x[index] = "┰"
    markedTBar = "─┬" + "".join(x) + "\n"
    x[index] = "┸"
    markedBBar = "─┴" + "".join(x)

    if not r.ok:
        return None

    try:
        j = r.json()
    except:
        return None

    days = []
    try:
        data = {
            'days': []
        }


        for day in j['weather']:
            date = day['date'].split('-')
            m = const.months[int(date[1])-1]
            d = date[2]
            dInt = int(d)

            average = day["avgtempC"]
            high = day["maxtempC"]
            low = day["mintempC"]
            uvIndex = day["uvIndex"]

            s = f"{m} {d}: {high}/{average}/{low}℃ - UV:{uvIndex}\n"


            tBar = "─┬────────────────────────────────\n" if dInt != currentDay else markedTBar
            l =   ["H│",
                   "I│",
                   "T│",
                   "P│"]
            bBar = "─┴────────────────────────────────" if dInt != currentDay else markedBBar

            s +=  tBar

            totalPercip = 0
            for hour in day['hourly']:
                time = padChar(int(hour['time'])//100," ", 4)
                i,size = const.WEATHER_SYMBOL[const.WWO_CODE[hour['weatherCode']]]
                icon = i + " "*(4-size)
                temp = padChar(hour['tempC']," ", 4)
                mm   = padChar(round(float(hour['precipMM']),1)," ", 4)
                l[0] += time
                l[1] += icon
                l[2] += temp
                l[3] += mm
                totalPercip += float(mm)

            s += '\n'.join(l) + '\n'
            s +=  bBar
            days.append(s)
            data['days'].append({
                'temp': average,
                'high': high,
                'low': low,
                'uvIndex': uvIndex,
                'percip': round(totalPercip, 2),
            })

    except KeyError:
        return None

    s = '\n\n'.join(days) + f"\n(H)our, (I)con, (T)emp, (P)recip"
    res = {
        'str': s,
        'data': data,
    }
    return res


def getCurrentWeather():
    # prevent spamming wttrin while testing
    if not const.isRpi():
        return None

    r = requests.get(const.wttrCurrentData, timeout=const.requestTimeout)
    if not r.ok:
        return None

    text, temp, feelsLike, humid, percip3h, uv = r.text.split('\n')
    #text, temp, feelsLike, humid, percip3h, uv, sunrise, sunset = r.text.split('\n')
    text = text.lower().replace("unknown precipitation", "precip")

    temp, feelsLike = int(temp[:-2]), int(feelsLike[:-2])
    humid = humid[:-1]
    percip3h = round(float(percip3h[:-2]), 2)

    #sunrise = roundTimeStr(sunrise)
    #sunset = roundTimeStr(sunset)

    res = {
        #'str': f'{text} {temp}C({feelsLike}C) {humid}%',
        'str': f'{temp}C({feelsLike}C) {humid}%',
        'data': {
            'text': text,
            'temp': temp,
            'feelsLike': feelsLike,
            'humid': humid,
            'percip3h': percip3h,
            'uv': uv,
            #'sunrise': sunrise,
            #'sunset': sunset,
            },
    }
    return res

def getWeatherImageLocal():
    r = requests.get(const.weatherUrl, timeout=const.requestTimeout)
    if not r.ok:
        return None

    lines = r.text.split('\n')[0:-1]
    s = '\n'.join(lines)

    res = {
        'str': s,
        'data': {},
    }
    return res


def getIndoorClimateBMELocal():
    data = getBME()
    if data is None:
        s = f'T: N/A \nH: N/A \nP: N/A'
        res = {
            'str':s,
            'data':{},
        }
    else:
        s = f'T: {data.temp} \nH: {data.humid} \nP: {data.pressure}'
        res = {
            'str':s,
            'data':{'temp':round(data.temp), 'humid': round(data.humid), 'pressure': round(data.pressure)},
        }
    return res

def getIndoorClimateDHTLocal():
    data = getDHT()
    if data is None:
        s = f'Temprature: N/A \nHumidity: N/A'
        res = {
            'str':s,
            'data':{},
        }
    else:
        s = f'T: {data.temp} \nH: {data.humid}'
        res = {
            'str':s,
            'data':{'temp':round(data.temp), 'humid': round(data.humid)},
        }
    return res

def getWeatherServerLocal(ip:str):
    data = getWeatherServerData(ip)

    if data is None:
        s = f'T: N/A \nH: N/A \nP: N/A'
        res = {
            'str':s,
            'data':{},
        }
    else:
        s = f'T: {data.temp} \nH: {data.humid} \nP: {data.pressure}'
        res = {
            'str':s,
            'data':data.toJson(),
        }
    return res

def getAirQualityServerLocal(ip:str):
    data = getAirQualityServerData(ip)

    if data is None:
        s = f'T:     N/A \nH:     N/A \nP:     N/A \nIQA:   N/A \nVOC:   N/A \nPM1:   N/A \nPM2.5: N/A \nPM10:  N/A \nCo2:   N/A'
        res = {
            'str':s,
            'data':{},
        }
    else:
        s = f'T:     {data.temp} \nH:     {data.humid} \nP:     {data.pressure} \nIQA:   {data.iaq} \nVOC:   {data.voc} \nPM1:   {data.pm1} \nPM2.5: {data.pm2_5} \nPM10:  {data.pm10} \nCo2:   {data.co2}'
        res = {
            'str':s,
            'data':data.toJson(),
        }
    return res

def getClockLocal():
    now = datetime.now()
    clock = now.strftime("%I:%M %p")
    date =  now.strftime("%b %-d")
    day =  now.strftime("%a")
    res = {
        'str': f'{clock} {date}',
        'data':{'clock': clock, 'date': date, 'day': day},
    }
    return res

def getServerVersion():
    res = {
        'str': f'{__version__}',
        'data':{'version': __version__},
    }
    return res

def getJobLog():
    s = ""
    for job in jobLog:
        s += f'{job}\n'
    res = {
        'str': s,
        'data':{},
    }
    return res

def getRfLog():
    s = ""
    for rf in rfLog:
        s += f'{rf}\n'
    res = {
        'str': s,
        'data':{},
    }
    return res

dataSources = [
    {
        'name': 'USD → CAD',
        'color': 'green',
        'url': '/api/data/forex/usd/cad',
        'local': lambda: cached(getForexLocal, 5*60//2, src = 'usd', dest = 'cad'),
        'pollingPeriod': 5*60,

        'dashboard':{
            'enabled':True,
        },

        'values': {
            'usd-cad': {
                'enabled': True,
                'dataPath': ['data', 'rate']
            }
        },
    },

    {
        'name': 'clock',
        'local': getClockLocal,
        'pollingPeriod': 1,

        'values': {
            'clock': {
                'dataPath': ['data', 'clock'],
                'enabled': True,
            },
            'date': {
                'dataPath': ['data', 'date'],
                'enabled': True,
            },
            'day': {
                'dataPath': ['data', 'day'],
                'enabled': True,
            }
        }

    },

    {
        'name': 'AQ Station',
        'color': 'yellow',
        'url': f'/api/data/aq',
        'local': lambda: cached(getAirQualityServerLocal, 60//2, ip=const.airQualityServerIP),
        'pollingPeriod': 60,
        'dashboard':{
            'enabled': True,
        },
        'values': {
            'aq-temp': {
                'dataPath': ['data', 'temp'],
                'enabled': True,
            },
            'aq-humid': {
                'dataPath': ['data', 'humid'],
                'enabled': True,
            },
            'aq-pressure': {
                'dataPath': ['data', 'pressure'],
                'enabled': True,
            },
            'aq-iaq': {
                'dataPath': ['data', 'iaq'],
                'enabled': True,
            },
            'aq-co2Eq': {
                'dataPath': ['data', 'co2Eq'],
                'enabled': True,
            },
            'aq-voc': {
                'dataPath': ['data', 'voc'],
                'enabled': True,
            },
            'aq-pm1': {
                'dataPath': ['data', 'pm1'],
                'enabled': True,
            },
            'aq-pm2.5': {
                'dataPath': ['data', 'pm2.5'],
                'enabled': True,
            },
            'aq-pm10': {
                'dataPath': ['data', 'pm10'],
                'enabled': True,
            },
            'aq-co2': {
                'dataPath': ['data', 'co2'],
                'enabled': True,
            },
        }
    },

    {
        'name': 'Indoor',
        'color': 'blue',
        'url': f'/api/data/temp-humid/indoor',
        'local':
            ( lambda: cached(getIndoorClimateBMELocal,30//2) ) if const.useBME else
            ( lambda: cached(getIndoorClimateDHTLocal,30//2) ) if const.useDht22 else
            ( lambda: cached(getWeatherServerLocal,(3*60)//2, ip=const.indoorWeatherServerIp) )
            ,
        'pollingPeriod': 30 if const.useBME or const.useDht22 else 3*60,

        'dashboard':{
            'enabled': True,
        },

        'values': {
            'temp': {
                'dataPath': ['data', 'temp'],
                'enabled': True,
            },
            'humid': {
                'dataPath': ['data', 'humid'],
                'enabled': True,
            },
            'pressure': {
                'dataPath': ['data', 'pressure'],
                'enabled': True,
            }
        } if const.useBME or not const.useDht22 else {
            'temp': {
                'dataPath': ['data', 'temp'],
                'enabled': True,
            },
            'humid': {
                'dataPath': ['data', 'humid'],
                'enabled': True,
            }
        }
    },
    {
        'name': 'Outdoor',
        'color': 'purple',
        'url': f'/api/data/temp-humid/outdoor',
        'local': lambda: cached(getWeatherServerLocal,(3*60)//2, ip = const.outdoorWeatherServerIp),
        'pollingPeriod': 3*60,

        'dashboard':{
            'enabled': True,
        },

        'values': {
            'outdoorTemp': {
                'dataPath': ['data', 'temp'],
                'enabled': True,
            },
            'outdoorHumid': {
                'dataPath': ['data', 'humid'],
                'enabled': True,
            },
            'outdoorPressure': {
                'dataPath': ['data', 'pressure'],
                'enabled': True,
            }
        }
    },
    {
        'name': 'Printer',
        'color': 'red',
        'url': f'/api/data/temp-humid/printer',
        'local': lambda: cached(getWeatherServerLocal,(60)//2, ip=const.printChamberWeatherServerIp),
        'pollingPeriod': 60,

        'dashboard':{
            'enabled': True,
        },

        'values': {
            'printerTemp': {
                'dataPath': ['data', 'temp'],
                'enabled': True,
            },
            'printerHumid': {
                'dataPath': ['data', 'humid'],
                'enabled': True,
            },
            'printerPressure': {
                'dataPath': ['data', 'pressure'],
                'enabled': False,
            }
        }
    },
    {
        'name': 'Office',
        'color': 'yellow',
        'url': f'/api/data/temp-humid/office',
        'local': lambda: cached(getWeatherServerLocal,(60)//2, ip=const.officeChamberWeatherServerIp),
        'pollingPeriod': 60,

        'dashboard':{
            'enabled': True,
        },

        'values': {
            'officeTemp': {
                'dataPath': ['data', 'temp'],
                'enabled': True,
            },
            'officeHumid': {
                'dataPath': ['data', 'humid'],
                'enabled': True,
            },
            'officePressure': {
                'dataPath': ['data', 'pressure'],
                'enabled': False,
            }
        }
    },

    {
        'name': 'Weather',
        'color': 'blue',
        'url': f'/api/data/weatherImage',
        'local': lambda: cached(getWeatherImageLocal, 10*60//2),
        'pollingPeriod': 10*60,

        'dashboard':{
            'enabled':False,
        },
        'values': {
        }
    },

    {
        'name': 'Forecast',
        'color': 'purple',
        'url': f'/api/data/forecast',
        'local': lambda: cached(getForecastLocal, 10*60//2),
        'pollingPeriod': 10*60,

        'dashboard':{
            'enabled': True,
            'hideable': True,
        },

        'values': {
            'wttrTotalPercip': {
                'enabled': True,
                'dataPath': ['data', 'days', 0, 'percip']
            },
            'wttrTempTomorrow': {
                'enabled': True,
                'dataPath': ['data', 'days', 1, 'temp']
            },
            'wttrTomorrowPercip': {
                'enabled': True,
                'dataPath': ['data', 'days', 1, 'percip']
            },
        },
    },

    {
        'name': 'Current',
        'color': 'blue',
        'url': f'/api/data/current-weather',
        'local': lambda: cached(getCurrentWeather, 10*60//2),
        'pollingPeriod': 10*60,

        'dashboard':{
            'enabled': False,
        },

        'values': {
            'wttrText': {
                'enabled': True,
                'dataPath': ['data', 'text']
            },
            'wttrTemp': {
                'enabled': True,
                'dataPath': ['data', 'temp']
            },
            'wttrHumid': {
                'enabled': True,
                'dataPath': ['data', 'humid']
            },
            'wttrUV': {
                'enabled': True,
                'dataPath': ['data', 'uv']
            },
            'wttrPercip3h': {
                'enabled': True,
                'dataPath': ['data', 'percip3h']
            },
            'wttrFeelsLike': {
                'enabled': True,
                'dataPath': ['data', 'feelsLike']
            },
            #'wttrSunrise': {
            #    'enabled': True,
            #    'dataPath': ['data', 'sunrise']
            #},
            #'wttrSunset': {
            #    'enabled': True,
            #    'dataPath': ['data', 'sunset']
            #},
        },
    },

    {
        'name': 'Errors',
        'color': 'red',
        'url': '/api/data/errors',
        'local': getErrors,
        'pollingPeriod': 15,

        'dashboard':{
            'enabled':True,
            'buttons':[{
                'text': 'Clear',
                'actions':[
                    {'type':'request', 'route':'api/dashboard/errors' , 'method': 'DELETE', 'data':{}},
                    {'type': 'reload'},
                 ],
            }],
        },

        'values': {
            'anyErrors': {
                'enabled': True,
                'dataPath': ['data', 'anyErrors']
            },
        },
    },
    {
        'name': 'Version',
        'color': 'gray',
        'url': '/api/data/version',
        'local': getServerVersion,
        'pollingPeriod': 10*60,

        'dashboard':{
            'enabled':True,
        },

        'values': {
            'version': {
                'enabled': False,
                'dataPath': ['data', 'version']
            }
        },
    },
    {
        'name': 'Job Log',
        'color': 'gray',
        'url': '/api/data/job-log',
        'local': getJobLog,
        'pollingPeriod': 3*60,

        'dashboard':{
            'enabled':True,
            'hideable': True,
            'buttons':[{
                'text': 'Clear',
                'actions':[
                    {'type':'request', 'route':'api/dashboard/logs' , 'method': 'DELETE', 'data':{'name':'jobLog'}},
                    {'type': 'reload'},
                 ],
            }],
        },

        'values': {
        },
    },
    {
        'name': 'RF Log',
        'color': 'gray',
        'url': '/api/data/rf-log',
        'local': getRfLog,
        'pollingPeriod': 3*60,

        'dashboard':{
            'enabled':True,
            'hideable': True,
            'buttons':[{
                'text': 'Clear',
                'actions':[
                    {'type':'request', 'route':'api/dashboard/logs' , 'method': 'DELETE', 'data':{'name':'rfLog'}},
                    {'type': 'reload'},
                ],
            }],
        },

        'values': {
        },
    },


]
# add str to value
for source in dataSources:
    if 'values' not in source:
        source['values'] = {}
    source['values'][f"{source['name']}-str"] = {'enabled':False, 'dataPath': ['str']}

dataSourceValues = set() # a set of all value keys (ie temp, humid, ...)
dataSourceDict = {} # name: {source} (ie "Indoor": {"name": "Indoor", "color": "blue", "pollingPeriod": ...})
for source in dataSources:
    assert 'name' in source
    dataSourceDict[source['name']] = source
    if 'values' not in source:
        continue
    for value in source['values']:
        if source['values'][value]['enabled']:
            dataSourceValues.add(value)


def getSources(valueKeys: list):
    res = []

    for source in dataSources:
        if not 'values' in source:
            continue
        for key in valueKeys:
            if key in source['values']:
                res.append(source)
                break
    return res

def getSourceDict(valueKeys: set):
    res = {}

    for name, source in dataSourceDict.items():
        if not 'values' in source:
            continue
        for key in source['values']:
            if key in valueKeys:
                res[name] = source
                break
    return res

# gets polling period of the source that yeilds provided value
def getPollingPeriod(valueKey:str) -> Union[int, None]:
    for source in dataSources:
        if not 'values' in source:
            continue
        if not 'pollingPeriod' in source:
            continue
        if not valueKey in source['values']:
            continue
        return source['pollingPeriod']
    return None



