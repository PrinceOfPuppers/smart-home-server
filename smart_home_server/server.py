from flask import Flask, send_from_directory, render_template

from smart_home_server.threads.scheduler import startScheduler, stopScheduler, joinScheduler, getJobs
from smart_home_server.threads.presser import startPresser, stopPresser, joinPresser
from smart_home_server.threads.lcd import stopLCD, joinLCD, startUpdateLCD
from smart_home_server import InterruptTriggered
import smart_home_server.constants as const

from smart_home_server.api.schedule import scheduleApi
from smart_home_server.api.remote import remoteApi
from smart_home_server.api.dashboard import dashboardApi

app = Flask(__name__)
app.register_blueprint(scheduleApi)
app.register_blueprint(remoteApi)
app.register_blueprint(dashboardApi)

@app.route('/<path:path>')
def send_templates(path):
   return send_from_directory(const.staticFolder, path)

@app.route('/remote')
def lightsGet():
    return render_template('remote.html', channels=[i for i in range(len(const.txChannels))])

@app.route('/schedule')
def scheduleGet():
    jobs = getJobs()
    return render_template('schedule.html', minChannel=0, maxChannel=len(const.txChannels)-1, jobs=jobs)

@app.route('/dashboard')
def dashboardGet():
    return render_template('dashboard.html', dashboardElements=[element for element in const.dashboardElements if element['enabled']])


def startServer():
    global app
    try:
        startPresser()
        startScheduler()
        startUpdateLCD(fromFile=True)
        app.run(host='0.0.0.0', port=5000)
    except InterruptTriggered:
        pass
    finally:
        stopPresser()
        stopScheduler()
        stopLCD()
        joinPresser()
        joinScheduler()
        joinLCD()

if __name__ == '__main__':
    startServer()
