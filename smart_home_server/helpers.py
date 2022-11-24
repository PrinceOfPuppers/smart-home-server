from queue import Queue
import requests
import string

import smart_home_server.constants as const

def clearQueue(q: Queue):
    with q.mutex:
        q.queue.clear()

def padZeros(num, length):
    numStr = str(num)
    return f'{"0"*(length - len(numStr))}{numStr}' if len(numStr) < length else numStr

def padChar(s, c, length):
    s = str(s)
    res = f'{s}{c*(length - len(s))}' if len(s) < length else s
    return res

def addDefault(data:dict, key:str, val):
    if key not in data:
        data[key] = val

def getAtTime(scheduledJob:dict):
    # formats: 
    # seconds   -> None
    # minutes   -> :SS
    # hours     -> MM:SS
    # otherwise -> HH:MM:SS 

    hasSeconds = "atSeconds" in scheduledJob
    hasMinutes = "atMinutes" in scheduledJob
    hasHours   = "atHours"   in scheduledJob

    seconds = padZeros(scheduledJob["atSeconds"], 2) if hasSeconds else "00" 
    minutes = padZeros(scheduledJob["atMinutes"], 2) if hasMinutes else "00" 
    hours   = padZeros(scheduledJob["atHours"]  , 2) if hasHours   else "00" 

    u = scheduledJob['unit']
    if u == 'seconds':
        return None

    s = f':{seconds}'

    if u == 'minute':
        if hasSeconds:
            return s
        return None

    s = f"{minutes}" + s
    if u == 'hours':
        if hasSeconds or hasMinutes:
            return s
        return None

    s = f"{hours}:" + s
    if hasSeconds or hasMinutes or hasHours:
        return s
    return None


def getExchangeRate(src,dest, decimal=3):
    r = requests.get(f'https://www.google.com/search?q={src}+to+{dest}', headers=const.fakeUserAgentHeaders)
    if not r.ok:
        return None
    x = const.googleExchangeRateDiv.search(r.text)
    if not x:
        return None
    
    res = x.group(1)
    return str(round(float(res),decimal))


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

def getForecastStr(url):
    r = requests.get(url)
    if not r.ok:
        return None

    j = r.json()
    days = []
    

    for day in j['weather']:
        date = day['date'].split('-')
        m = months[int(date[1])-1]
        d = date[2]
        
        average = day["avgtempC"]
        high = day["maxtempC"]
        low = day["mintempC"]
        uvIndex = day["uvIndex"]

        s = f"{m} {d}: {high}/{average}/{low}℃ - UV:{uvIndex}\n"
        s += "─┬───────────────────────────────\n"
        l =  ["H│",
              "I│", 
              "T│", 
              "P│"]

        for hour in day['hourly']:
            time = padChar(int(hour['time'])//100," ", 4)
            i,size = WEATHER_SYMBOL[WWO_CODE[hour['weatherCode']]]
            icon = i + " "*(4-size)
            temp = padChar(hour['tempC']," ", 4)
            mm   = padChar(round(float(hour['precipMM']),1)," ", 4)
            l[0] += time
            l[1] += icon
            l[2] += temp
            l[3] += mm

        s += '\n'.join(l) + '\n'
        s += "─┴───────────────────────────────"
        days.append(s)

    return '\n\n'.join(days) + f"\n(H)our, (I)con, (T)emp, (P)recip"#\n{const.fullForcastUrl}\n{const.forecastUrlV2}"


