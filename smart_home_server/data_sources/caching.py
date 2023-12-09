from datetime import datetime, timedelta
from threading import Lock

from typing import Callable

_cache = {}
_cacheLock = Lock()

def cached(func:Callable, cacheDuration:float, **kwargs):
    global _cache
    global _cacheLock

    rep = str(id(func)) + str(sorted(kwargs.items()))

    # use cache lock to aquire specific func lock
    _cacheLock.acquire()
    if rep in _cache:
        lock = _cache[rep]['lock']
    else:
        lock = Lock()
        _cache[rep] = {'lock': lock}
    _cacheLock.release()


    lock.acquire()
    try:
        now = datetime.now()

        if 'lastUpdate' in _cache[rep]:
            lastUpdate = _cache[rep]['lastUpdate']
            oldVal = _cache[rep]['val']

            cacheExprDT = timedelta(seconds=cacheDuration)
            timeTillExprDT = cacheExprDT + lastUpdate - now
            if timeTillExprDT > timedelta(seconds=0):
                val = oldVal
            else:
                val = func(**kwargs)
                _cache[rep]['lastUpdate'] = now
                _cache[rep]['val'] = val
        else:
            val = func(**kwargs)
            _cache[rep]['val'] = val
            _cache[rep]['lastUpdate'] = now

    finally:
        lock.release()
    return val


