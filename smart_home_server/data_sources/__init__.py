import requests
from datetime import datetime

from smart_home_server.hardware_interfaces.lcd import getLCDFMT
from smart_home_server.hardware_interfaces.dht22 import getDHT
from smart_home_server.helpers import stripLines, padChar
import smart_home_server.constants as const

# return format is 
#example = {
#    'data': {
#        "temp": 123,
#        "humid": 123
#    },
#    'str': f'Temprature: 123 \nHumidity: 123'
#    'pollingPeriod': 60*10
#}

def getForexLocal(src,dest, decimal=3):
    try:
        r = requests.get(f'https://www.google.com/search?q={src}+to+{dest}', headers=const.fakeUserAgentHeaders)
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
    r = requests.get(const.wttrApiUrl)
    if not r.ok:
        return None

    j = r.json()
    days = []
    try:
        current = j['current_condition'][0]
        data = {
            'current': {
                "temp": float(current['temp_C']),
                "humid": float(current['humidity']),
                "text": const.WWO_CODE[current['weatherCode']],
                "UV": int(current['uvIndex']),
                "percip": float(current['precipMM']),
                "feelsLike": float(current['FeelsLikeC']),
            },
            'days': []
        }


        for day in j['weather']:
            date = day['date'].split('-')
            m = const.months[int(date[1])-1]
            d = date[2]

            average = day["avgtempC"]
            high = day["maxtempC"]
            low = day["mintempC"]
            uvIndex = day["uvIndex"]

            s = f"{m} {d}: {high}/{average}/{low}℃ - UV:{uvIndex}\n"

            s +=  "─┬───────────────────────────────\n"
            l =  ["H│",
                  "I│",
                  "T│",
                  "P│"]

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
            s +=  "─┴───────────────────────────────"
            days.append(s)
            data['days'].append({
                'temp': average,
                'high': high,
                'low': low,
                'uvIndex': uvIndex,
                'percip': totalPercip,
            })

    except KeyError:
        return None

    s = '\n\n'.join(days) + f"\n(H)our, (I)con, (T)emp, (P)recip"
    res = {
        'str': s,
        'data': data,
    }
    return res



def getWeatherImageLocal():
    r = requests.get(const.weatherUrl)
    if not r.ok:
        return None
    s = stripLines(r.text,0,-1)
    res = {
        'str': s,
        'data': {},
    }
    return res

def getLCDLocal():
    s = getLCDFMT()
    res = {
        'str': s,
        'data': {},
    }
    return res

def getIndoorClimateLocal():
    data = getDHT()
    if data is None:
        s = f'Temprature: N/A \nHumidity: N/A'
        res = {
            'str':s,
            'data':{},
        }
    else:
        s = f'Temprature: {data.temp} \nHumidity: {data.humid}'
        res = {
            'str':s,
            'data':{'temp':data.temp, 'humid': data.humid},
        }
    return res

def getClockLocal():
    now = datetime.now()
    clock = now.strftime("%I:%M")
    date =  now.strftime("%b %-d")
    res = {
        'str': f'{clock} {date}',
        'data':{'clock': clock, 'date': date},
    }
    return res



dataSources = [
    {
        'url': '/api/data/forex/usd/cad',
        'local': lambda: getForexLocal('usd', 'cad'),
        'pollingPeriod': 5*60,

        'dashboard':{
            'name': 'USD → CAD',
            'enabled':True,
            'color': 'green',
        },

        'values': {
            'usd->cad': {
                'enabled': True,
                'dataPath': ['data', 'rate']
            }
        },
    },

    {
        'url': f'/api/data/weatherImage',
        'local': getWeatherImageLocal,
        'pollingPeriod': 10*60,

        'dashboard':{
            'name': 'Weather',
            'enabled':False,
            'color': 'blue',
        }
    },

    {
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
            }
        }

    },

    {
        'url': f'/api/data/forecast',
        'local': getForecastLocal,
        'pollingPeriod': 10*60,

        'dashboard':{
            'name': 'Forecast',
            'enabled': True,
            'color': 'blue',

        },

        'values': {
            'wttrTemp': {
                'enabled': True,
                'dataPath': ['data', 'current', 'temp']
            },
            'wttrHumid': {
                'enabled': True,
                'dataPath': ['data', 'current', 'humid']
            },
            'wttrText': {
                'enabled': True,
                'dataPath': ['data', 'current', 'text']
            },
            'wttrUV': {
                'enabled': True,
                'dataPath': ['data', 'current', 'UV']
            },
            'wttrPercip': {
                'enabled': True,
                'dataPath': ['data', 'current', 'UV']
            },
            'wttrFeelsLike': {
                'enabled': True,
                'dataPath': ['data', 'current', 'feelsLike']
            },
        },
    },

    # has bespoke solution in frontend
    {
        'url': f'/api/data/lcd',
        'local': getLCDLocal,
        'pollingPeriod': 10*60,

        'dashboard':{
            'name': 'LCD',
            'enabled': False, #handled in frontend
            'color': 'purple',

        }
    },


    {
        'url': f'/api/data/temp-humid',
        'local': getIndoorClimateLocal,
        'pollingPeriod': 31,

        'dashboard':{
            'name': 'Indoor Climate',
            'enabled': True,
            'color': 'yellow',
        },

        'values': {
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
]
