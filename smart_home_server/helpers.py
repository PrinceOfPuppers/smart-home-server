from queue import Queue

def clearQueue(q: Queue):
    with q.mutex:
        q.queue.clear()

def padZeros(num, length):
    numStr = str(num)
    return f'{"0"*(length - len(numStr))}{numStr}' if len(numStr) < length else numStr

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

