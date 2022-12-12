from flask_sock import Sock
from simple_websocket import ConnectionClosed
from functools import partial
import json

from smart_home_server.data_sources import dataSources
from smart_home_server.threads.subscribeManager import subscribe
import smart_home_server.constants as const

dataSourcesSocket = Sock()

x=''
for i,source in enumerate(dataSources):
    if 'dashboard' not in source:
        continue
    if 'url' not in source:
        continue
    x += f'@dataSourcesSocket.route(\'{source["url"]}\')\n' \
         f'def f_onConnect_{i}(ws, i={i}):\n'

    x += \
'''
    source=dataSources[i]
    dash = source['dashboard']
    value = f'{source["name"]}-str'
    print(f'sock conn: {value}')
    values = [value]

    unsub=False
    def sendData(data):
        try:
            ws.send(data[value])
        except:
            unsub=True

    subscribe(\
        values,
        sendData,
        lambda: unsub,
        lambda: print(f"{dash['name']} Error")
    )
    try:
        while not unsub:
            ws.receive(timeout=const.threadPollingPeriod)
    finally:
        unsub=True
        print(f'sock unsub: {value}')
    ws.close()

'''
exec(x)
