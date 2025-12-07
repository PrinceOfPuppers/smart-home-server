import requests
from datetime import datetime
from typing import Union

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


from dataclasses import dataclass, asdict, field
from abc import abstractmethod
from enum import Enum


class DatasourceColor(Enum):
    GREEN = 'green'
    YELLOW = 'yellow'
    PURPLE = 'purple'
    BLUE = 'blue'
    RED = 'red'
    GRAY = 'gray'
    # TODO: ensure exaustive

@dataclass 
class DatasourceDashboard:
    label: str # used on dashboard
    enabled: bool = True
    hideable: bool = False

@dataclass
class DatasourceValue:
    dataPath: list
    enabled: bool = True

# allows properties to be read by asdict
@dataclass
class _Datasource:
    url: str = field(init=False)
    values: dict[str, DatasourceValue] = field(init=False)

@dataclass(kw_only=True)
class Datasource(_Datasource):
    name:str # used for url and regex, must be unique
    color:DatasourceColor
    pollingPeriod: int
    dashboard: DatasourceDashboard

    @property
    def url(self) -> str: # pyright: ignore
        return f"api/data/{self.name}"

    @property
    def buttons(self) -> list:
        return []

    @property
    def values(self) -> dict[str, DatasourceValue]: # pyright: ignore
        return {}

    @abstractmethod
    def local(self):
        return {}

    def _value_helper(self, vals:set[str]):
        return {
            f"{self.name}-{val}": DatasourceValue(dataPath = ['data', val]) for val in vals
        }


@dataclass
class DatasourceForex(Datasource):
    src: str
    dest: str
    pollingPeriod:int = 5*60

    @property
    def values(self):
        return {
            f"{self.name}": DatasourceValue(dataPath = ['data', 'rate'])
        }

    def local(self):
        return cached(getForexLocal, self.pollingPeriod//2, src = self.src, dest = self.dest)

@dataclass
class DatasourceClock(Datasource):
    pollingPeriod:int = 1

    @property
    def values(self):
        return self._value_helper({'time', 'date', 'day'})

    def local(self):
        return getClockLocal()

@dataclass
class DatasourceAQ(Datasource):
    ip:str
    pollingPeriod:int = 60

    @property
    def values(self):
        return self._value_helper({'temp', 'humid', 'pressure', 'iaq', 'co2Eq', 'voc', 'pm1', 'pm2.5', 'pm10', 'co2'})

    def local(self):
        return cached(getAirQualityServerLocal, self.pollingPeriod//2, ip=self.ip)

@dataclass 
class DatasourceTempHumid(Datasource):
    ip:str
    pollingPeriod:int = 60

    @property
    def values(self):
        return self._value_helper({'temp', 'humid', 'pressure'})

    def local(self):
        return cached(getAirQualityServerLocal, self.pollingPeriod//2, ip=self.ip)

@dataclass 
class DatasourceWeatherImage(Datasource):
    pollingPeriod:int = 10*60

    @property
    def values(self):
        return {}

    def local(self):
        return cached(getWeatherImageLocal, self.pollingPeriod//2)


@dataclass 
class DatasourceForcast(Datasource):
    pollingPeriod:int = 10*60

    @property
    def values(self):
        return {
            f'{self.name}-totalPercip': DatasourceValue(dataPath = ['data', 'days', 0, 'percip']),
            f'{self.name}-tomorrowTemp': DatasourceValue(dataPath = ['data', 'days', 1, 'temp']),
            f'{self.name}-tomorrowPercip': DatasourceValue(dataPath = ['data', 'days', 1, 'percip']),
        }

    def local(self):
        return cached(getForecastLocal, self.pollingPeriod//2)

@dataclass 
class DatasourceWeatherCurrent(Datasource):
    pollingPeriod:int = 10*60

    @property
    def values(self):
        return self._value_helper({'text', 'temp', 'humid', "uv", 'percip3h', 'feelsLike', 'sunrise', 'sunset'})

    def local(self):
        return cached(getCurrentWeather, self.pollingPeriod//2)

@dataclass 
class DatasourceErrors(Datasource):
    pollingPeriod:int = 15

    @property
    def values(self):
        return self._value_helper({'anyErrs'})

    def local(self):
        return getErrors()

    @property
    def buttons(self):
        return [{
            'text': 'Clear',
            'actions':[
                {'type':'request', 'route':'api/dashboard/errors' , 'method': 'DELETE', 'data':{}},
                {'type': 'reload'},
             ],
        }]
        
@dataclass 
class DatasourceJobLog(Datasource):
    pollingPeriod:int = 30*60

    def local(self):
        return getJobLog()

    @property
    def buttons(self):
        return [{
                'text': 'Clear',
                'actions':[
                    {'type':'request', 'route':'api/dashboard/logs' , 'method': 'DELETE', 'data':{'name':'jobLog'}},
                    {'type': 'reload'},
                 ],
            }]

@dataclass 
class DatasourceRfLog(Datasource):
    pollingPeriod:int = 30*60

    def local(self):
        return getRfLog()

    @property
    def buttons(self):
        return [{
                'text': 'Clear',
                'actions':[
                    {'type':'request', 'route':'api/dashboard/logs' , 'method': 'DELETE', 'data':{'name':'rfLog'}},
                    {'type': 'reload'},
                 ],
            }]

@dataclass
class DatasourceVersion(Datasource):
    pollingPeriod:int = 10*60

    def local(self):
        return getServerVersion()

    @property
    def values(self):
        return self._value_helper({'version'})

dataSources = [
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



