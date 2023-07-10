from collections import deque

jobLog = deque([], maxlen=10)
rfLog = deque([], maxlen=10)
logs={'jobLog': jobLog, 'rfLog': rfLog}
