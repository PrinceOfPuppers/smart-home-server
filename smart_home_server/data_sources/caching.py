from datetime import datetime, timedelta
from threading import Lock

from typing import Callable

_cache = {}
_cacheLock = Lock()

def cached(func:Callable, cacheDuration:float, **kwargs):
    global _cache
    global _cacheLock

    # use cache lock to aquire specific func lock
    _cacheLock.acquire()
    if func in _cache:
        lock = _cache[func]['lock']
    else:
        lock = Lock()
        _cache[func] = {'lock': lock}
    _cacheLock.release()


    lock.acquire()
    now = datetime.now()

    if 'lastUpdate' in _cache[func]:
        lastUpdate = _cache[func]['lastUpdate']
        oldVal = _cache[func]['val']

        cacheExprDT = timedelta(seconds=cacheDuration)
        timeTillExprDT = cacheExprDT + lastUpdate - now
        if timeTillExprDT > timedelta(seconds=0):
            val = oldVal
        else:
            val = func(**kwargs)
            _cache[func]['lastUpdate'] = now
            _cache[func]['val'] = val
    else:
        val = func(**kwargs)
        _cache[func]['val'] = val
        _cache[func]['lastUpdate'] = now

    lock.release()
    return val


