import requests
from datetime import datetime

from pprint import pprint
from smart_home_server.hardware_interfaces.bme280 import getBME
from smart_home_server.hardware_interfaces.udp import getWeatherServerData, getAirQualityServerData
from smart_home_server.helpers import padChar
from threading import Lock
import smart_home_server.constants as const
from time import time

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

forexCache = {}
forexCacheLock = Lock()
def _getForexLocal(src, dest):
    try:
        if (src in forexCache) and \
           (forexCache[src]["time_next_update_unix"]) > time() and \
           (dest in forexCache[src]["rates"]):

            return forexCache[src]["rates"][dest]
    except:
        pass
    return None

def getForexLocal(src,dest, decimal=3):
    src = src.upper().strip()
    dest = dest.upper().strip()
    if len(src) != 3 or len(dest) != 3:
        return None

    with forexCacheLock:
        rate = _getForexLocal(src, dest)

        if rate is None:
            try:
                r = requests.get(const.forexUrl(src), timeout=const.requestTimeout)
                if not r.ok:
                    return None
                forexCache[src] = r.json()
            except:
                return None
            rate = _getForexLocal(src, dest)

    if rate is None:
        return None

    rate = round(float(rate), decimal)
    res = {
        'str': str(rate),
        'data': {
            'src': src,
            'dest': dest,
            'rate': rate,
        },
    }
    return res

def getForecastLocal(locale: str):
    # prevent spamming wttrin while testing
    if not const.isRpi():
        return None

    r = requests.get(const.wttrApiUrl(locale), timeout=const.requestTimeout)

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


def getCurrentWeather(locale: str):
    # prevent spamming wttrin while testing
    if not const.isRpi():
        return None

    r = requests.get(const.wttrCurrentData(locale), timeout=const.requestTimeout)
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

def getWeatherImageLocal(locale: str):
    r = requests.get(const.weatherUrl(locale), timeout=const.requestTimeout)
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
        'data':{'time': clock, 'date': date, 'day': day},
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

def getErrors():
    s, anyErr = getErrorStrAndBool()
    res = {
        'str': s,
        'data': {'anyErrs' : anyErr},
    }
    return res

