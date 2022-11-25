import requests
from datetime import datetime

from smart_home_server.helpers import WWO_CODE, getExchangeRate
from smart_home_server.hardware_interfaces.dht22 import getDHT
import smart_home_server.constants as const


wttrFmtArgs = {"wttrTemp", "wttrHumid", "wttrText", "wttrUV", "wttrPercip", "wttrFeelsLike"}
weatherPeriod = 10*60
def getWeatherReplacements(args:set, replacements:dict):
    # check if fmt has args
    if args.isdisjoint(wttrFmtArgs):
        return False

    r = requests.get(const.wttrApiUrl)
    if not r.ok:
        return True

    j = r.json()['current_condition'][0]

    replacements["wttrTemp"] = j['temp_C']
    replacements["wttrHumid"] = j['humidity']
    replacements["wttrText"] = WWO_CODE[j['weatherCode']]
    replacements["wttrUV"] = j['uvIndex']
    replacements["wttrPercip"] = j['precipMM']
    replacements["wttrFeelsLike"] = j['FeelsLikeC']

    return True

# anything with fmt {src->dest} will count
forexPeriod = 5*60
def getForexReplacements(args:set, replacements:dict):
    hasArgs = False

    for arg in args:
        pair = arg.split('->')
        if len(pair) != 2:
            continue
        hasArgs = True
        replacements[arg] = getExchangeRate(pair[0], pair[1])

    return hasArgs

tempHumidArgs = ['temp', "humid"]
tempHumidPeriod = 10
def getTempHumidReplacements(args:set, replacements:dict):
    if args.isdisjoint(tempHumidArgs):
        return False
    data = getDHT()
    if data is None:
        replacements["temp"] = 'NA'
        replacements["humid"] = 'NA'
        return True
    replacements["temp"] = data.temp
    replacements["humid"] = data.humid
    return True


clockArgs = ['clock', 'date']
clockPeriod = 1
def getClockReplacements(args:set, replacements:dict):
    if args.isdisjoint(clockArgs):
        return False
    now = datetime.now()
    #replacements["clock"] = now.strftime("%I:%M %p")
    replacements["clock"] = now.strftime("%I:%M")
    replacements["date"] =  now.strftime("%b %-d")
    return True


def getPeriodPairs(args, replacements):
    hasWttr      = getWeatherReplacements(args, replacements)
    hasForex     = getForexReplacements(args, replacements)
    hasTempHumid = getTempHumidReplacements(args, replacements)
    hasClock     = getClockReplacements(args, replacements)


    periods = [
        (weatherPeriod*hasWttr,        getWeatherReplacements),
        (forexPeriod*hasForex,         getForexReplacements),
        (tempHumidPeriod*hasTempHumid, getTempHumidReplacements),
        (clockPeriod*hasClock,         getClockReplacements)
    ]
    return list(filter(lambda x: x[0]>0, periods))

spaceFormat = "space"
def fillSpacesAndClamp(lines):
    res = []
    for i in range(min(len(lines), const.lcdLines)):
        line = lines[i]
        size = len(line.format(space=""))
        numSpaces = len(line.format(space=" ")) - size
        if numSpaces != 0:
            spaceSize = max((const.lcdWidth - size)//numSpaces, 0)
            line = line.format(space=" "*spaceSize)

        # clamp length
        line = line if len(line) <= const.lcdWidth else line[0:const.lcdWidth]
        res.append(line)

    return res


