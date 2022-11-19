from flask import Flask

from smart_home_server.threads.scheduler import startScheduler, stopScheduler, joinScheduler
from smart_home_server.threads.presser import startPresser, stopPresser, joinPresser
from smart_home_server import InterruptTriggered

from smart_home_server.api import api

app = Flask(__name__)
app.register_blueprint(api)


def startServer():
    global app
    try:
        startPresser()
        startScheduler()
        app.run()
    except InterruptTriggered:
        stopPresser()
        stopScheduler()
        joinPresser()
        joinScheduler()

if __name__ == '__main__':
    startServer()
