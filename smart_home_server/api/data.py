from flask_sock import Sock
from simple_websocket import ConnectionClosed
from functools import partial
import json

from smart_home_server.data_sources import dataSources
from smart_home_server.threads.subscribeManager import subscribe
import smart_home_server.constants as const

dataSourcesSocket = Sock()

def funcRenamer(f, name):
    f.__name__ = name
    return f

for source in dataSources:
    if 'dashboard' not in source:
        continue
    if 'url' not in source:
        continue

    def onConnect(ws, source):
        dash = source['dashboard']
        value = f'{source["name"]}-str'
        values = [value]

        unsub=False
        errors = 0
        def sendLambda(data):
            nonlocal unsub
            nonlocal errors

            try:
                ws.send(data[value]),
            except ConnectionClosed:
                unsub=False
            except Exception:
                if errors > 3:
                    unsub=False
                errors+=1

        subscribe(\
            values,
            sendLambda,
            lambda: unsub,
            lambda: print(f"{dash['name']} Error")
        )
        try:
            while ws.connected:
                ws.receive(timeout=const.threadPollingPeriod)
        finally:
            unsub=False

    dataSourcesSocket.route(source['url'])(f=funcRenamer(partial(onConnect, source=source), f"onConnect-{source['url']}"))

