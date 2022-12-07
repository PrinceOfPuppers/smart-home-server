import smart_home_server.constants as const
from datetime import datetime, timedelta
from time import sleep

from smart_home_server.data_sources import getSources, dataSourceValues

def dataFromDataPath(x, dataPath):
    y = x
    for p in dataPath:
        y = y[p]
    return y

def updateToSend(source, toSend):
    func = source['local']
    res = func()
    if res is None:
        return
    for key,value in source['values'].items():
        if value['enabled']:
            try:
                data = dataFromDataPath(res , value['dataPath'])
            except KeyError:
                continue
            toSend[key] = data



# cb will be passed a dict like this: {"temp": 123, "wttrFeelsLike": 234} for each value in values
# note additional argumens may be passed
# funciton is blocking, will run until cbLoopCondition returns false
def polledUpdate(values, cb, cbLoopCondition, cbError, stopOnError = False):
    sources = getSources([value for value in values if value in dataSourceValues])

    # remove sources which have no values enabled
    for i in reversed(range(len(sources))):
        source = sources[i]
        anyEnabled = False
        for key in source['values']:
            val = source['values'][key]
            if val['enabled']:
                anyEnabled=True
                break
        if not anyEnabled:
            sources.pop(i)

    toSend = {}

    for source in sources:
        while True:
            try:
                updateToSend(source, toSend)
                break
            except Exception:
                sleep(0.1)


    cb(toSend)
    lastUpdate = datetime.now()

    while cbLoopCondition():
        sleep(const.threadPollingPeriod)
        try:
            now = datetime.now()
            updateOccured = False
            for source in sources:
                period = source['pollingPeriod']
                if now < lastUpdate+timedelta(seconds=period):
                    continue

                updateOccured = True
                lastUpdate = datetime.now()
                updateToSend(source, toSend)

            if updateOccured:
                cb(toSend)


        except Exception as e:
            cbError(e)
            if stopOnError:
                break

