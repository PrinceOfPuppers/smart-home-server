from flask import Flask, send_from_directory, render_template

from smart_home_server.threads.scheduler import startScheduler, stopScheduler, joinScheduler
from smart_home_server.threads.presser import startPresser, stopPresser, joinPresser
from smart_home_server import InterruptTriggered
import smart_home_server.constants as const

from smart_home_server.api import api

app = Flask(__name__)
app.register_blueprint(api)

@app.route('/<path:path>')
def send_templates(path):
   return send_from_directory(const.staticFolder, path)

@app.route('/lights')
def lightsGet():
    return render_template('lights.html', list_header="Channels:", channels=[i for i in range(len(const.txChannels))])

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
