from flask import Flask, send_from_directory, render_template, redirect
from time import time

from smart_home_server.handlers.scheduler import startScheduler, stopScheduler, joinScheduler, getJobs
from smart_home_server.handlers.presser import startPresser, stopPresser, joinPresser, getRemotes
from smart_home_server.handlers.triggerManager import getTriggers
from smart_home_server.handlers.subscribeManager import startSubscribeManager, stopSubscribeManager, joinSubscribeManager
from smart_home_server.handlers.rfMacros import startMac, stopMac, joinMac
from smart_home_server.handlers.lcd import getLcds, startLcdListener, stopLcdListener, joinLcdListener
from smart_home_server.handlers.graphs import getGraphs, startGraphs, stopGraphs, joinGraphs, getOnMonitor, putOnMonitor
from smart_home_server.hardware_interfaces.buttons import stopGpio

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
from smart_home_server.api.graph import graphApi
from smart_home_server.api.lcd import lcdApi
from smart_home_server.api.datasource import datasourceApi
import smart_home_server.data_sources.datasourceInterface as dsi
import smart_home_server.data_sources.datasourceTypes as dst
import smart_home_server.constants as const

values = list(dsi.datasources.datavalues.keys())
values.sort()

app = Flask(__name__)
app.register_blueprint(scheduleApi)
app.register_blueprint(remoteApi)
app.register_blueprint(dashboardApi)
app.register_blueprint(triggerApi)
app.register_blueprint(dataApi)
app.register_blueprint(noteApi)
app.register_blueprint(macroApi)
app.register_blueprint(lcdApi)
app.register_blueprint(graphApi)
app.register_blueprint(datasourceApi)
app.jinja_env.add_extension('jinja2.ext.do')

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
    lcds = getLcds()

    return render_template('schedule.html', 
                           remotes=getRemotes(), 
                           jobs=jobs, 
                           timeUnits = timeUnits, 
                           macros=macros,
                           lcds=lcds,
                           values=values)

@app.route('/dashboard')
def dashboardGet():
    elements=[]
    for source in dsi.datasources.datasourceList:
        if source.dashboard.enabled:
            elements.append(source.toJson())
    return render_template('dashboard.html', dashboardElements=elements)

@app.route('/trigger')
def triggerGet():
    triggerJobs = getTriggers()
    macros = getMacros()
    lcds = getLcds()
    remotes = getRemotes()
    return render_template('trigger.html', values=values, comparisons=triggerComparisons, triggerJobs=triggerJobs, remotes=remotes, macros=macros, lcds=lcds)

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
    lcds = getLcds()
    remotes=getRemotes()
    return render_template('macros.html', macros=macros, remotes=remotes, delays=delays, lcds=lcds)

@app.route('/lcds')
def lcdsGet():
    lcds = getLcds(tagActive=True)
    lcds.sort(key=lambda element: element['num'])
    return render_template('lcds.html', lcds=lcds, values=values)

@app.route('/graphs')
def graphsGet():
    graphs = getGraphs()
    graphs.sort(key=lambda element: element['datasource'])
    idOnMonitor = getOnMonitor()
    return render_template('graphs.html', loadTime=round(time()), graphs=graphs, values=values, colors=["blue", "green", "orange", "red", "yellow", "purple", "grey", "white"], idOnMonitor=idOnMonitor)

@app.route('/datasources')
def datasourcesGet():
    datasources = []
    datasourceSchemas = dst.Datasource.getSchema()['oneOf']
    datasourceSchemaDict = dst.Datasource.getSchemaTypeDict()
    for source in dsi.datasourcesMutable.datasourceList:
        datasources.append(source.toJson())
    return render_template('datasources.html', datasources=datasources, datasourceSchemas=datasourceSchemas, datasourceSchemaDict=datasourceSchemaDict)

def startServer():
    global app
    try:
        startScheduler()
        startSubscribeManager()
        startPresser()
        startLcdListener()
        startMac()
        startGraphs()

        if const.isRpi():
            from waitress import serve
            serve(app)
        else:
            app.run(host='0.0.0.0', port=5000)

    except InterruptTriggered:
        print("Interrupt Triggered, Shutting Down...")

    finally:
        stopGraphs()
        stopSubscribeManager()
        stopPresser()
        stopScheduler()
        stopLcdListener()
        stopMac()
        joinGraphs()
        joinSubscribeManager()
        joinPresser()
        joinScheduler()
        joinMac()
        stopGpio()

if __name__ == '__main__':
    startServer()

