from flask import Flask, send_from_directory, render_template, redirect

from smart_home_server.handlers.scheduler import startScheduler, stopScheduler, joinScheduler, getJobs
from smart_home_server.handlers.presser import startPresser, stopPresser, joinPresser, getRemotes
from smart_home_server.handlers.lcd import startUpdateLCD
from smart_home_server.handlers.triggerManager import getTriggers
from smart_home_server.handlers.subscribeManager import startSubscribeManager, stopSubscribeManager, joinSubscribeManager
from smart_home_server.handlers.rfMacros import startMac, stopMac, joinMac

from smart_home_server.handlers.notes import getNotes
from smart_home_server.handlers.macros import getMacros
from smart_home_server.handlers import getDelays

from smart_home_server import InterruptTriggered

from smart_home_server.api.schedule import scheduleApi, timeUnits
from smart_home_server.api.remote import remoteApi
from smart_home_server.api.dashboard import dashboardApi
from smart_home_server.api.data import dataApi
from smart_home_server.api.trigger import triggerApi, triggerComparisons
from smart_home_server.api.note import noteApi
from smart_home_server.api.macro import macroApi
from smart_home_server.data_sources import dataSources, dataSourceValues
import smart_home_server.constants as const

values = list(dataSourceValues)
values.sort()

app = Flask(__name__)
app.register_blueprint(scheduleApi)
app.register_blueprint(remoteApi)
app.register_blueprint(dashboardApi)
app.register_blueprint(triggerApi)
app.register_blueprint(dataApi)
app.register_blueprint(noteApi)
app.register_blueprint(macroApi)

@app.route('/')
def index():
    return redirect("/dashboard", code=302)

@app.route('/<path:path>')
def send_templates(path):
   return send_from_directory(const.staticFolder, path)

@app.route('/remote')
def lightsGet():
    return render_template('remote.html', remotes = getRemotes())

@app.route('/schedule')
def scheduleGet():
    jobs = getJobs()
    macros = getMacros()

    return render_template('schedule.html', 
                           remotes=getRemotes(), 
                           jobs=jobs, 
                           timeUnits = timeUnits, 
                           macros=macros,
                           values=values)

@app.route('/dashboard')
def dashboardGet():
    elements=[]
    for source in dataSources:
        if 'dashboard' in source and source['dashboard']['enabled']:
            elements.append(
                {
                    'url': source['url'],
                    'pollingPeriod': source['pollingPeriod'],
                    'color': source['color'],
                    'name': source['name'],
                 }
            )
    return render_template('dashboard.html', dashboardElements=elements, values=values)

@app.route('/trigger')
def triggerGet():
    triggerJobs = getTriggers()
    macros = getMacros()
    return render_template('trigger.html', values=values, comparisons=triggerComparisons, triggerJobs=triggerJobs, remotes=getRemotes(), macros=macros)

@app.route('/notes')
def notesGet():
    notes = getNotes()
    notes.sort(key = lambda element: element['name'])
    return render_template('notes.html', notes=notes)

@app.route('/macros')
def macrosGet():
    macros = getMacros()
    macros.sort(key = lambda element: element['name'])
    delays = getDelays()
    return render_template('macros.html', macros=macros, remotes=getRemotes(), delays=delays)


def startServer():
    global app
    try:
        startScheduler()
        startSubscribeManager()
        startPresser()
        startUpdateLCD(fromFile=True)
        startMac()

        if const.isRpi():
            from waitress import serve
            serve(app)
        else:
            app.run(host='0.0.0.0', port=5000)

    except InterruptTriggered:
        print("Interrupt Triggered, Shutting Down...")

    finally:
        joinSubscribeManager()
        stopPresser()
        stopScheduler()
        stopSubscribeManager()
        stopMac()
        joinPresser()
        joinScheduler()
        joinMac()

if __name__ == '__main__':
    startServer()

