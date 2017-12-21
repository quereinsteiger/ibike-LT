################################################################################
# Dependencies & Modules
################################################################################

from threading import Lock
from flask import Flask, render_template, request, redirect, session
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
import datetime
import numpy as np
import sqlite3 as sql
from subprocess import Popen, PIPE
from apps import connection
import shelve
import logging
import logging.config
import time

################################################################################
# Global Configs
################################################################################
logging.config.fileConfig('./config/logging.conf')
logfile=logging.getLogger('logfile')
show=logging.getLogger('show')

async_mode = None

app=Flask(__name__)
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()


################################################################################
# Requests & Routing
################################################################################

@app.route("/")
def hello():
    now=datetime.datetime.now()
    timeString = now.strftime("%d.%m.%Y")
    verbindung=connection.verbindung()
    datensatz=verbindung.abfrage("Select ID From tblMessung")
    if datensatz==[]:
        id=1
    else:
        id=[]
        for ds in datensatz:
            id.append(ds['ID'])
        id=max(id)+1

    templateData={
        'title': 'iBike',
        'time': timeString,
        'Messung': id
        }
    return render_template('main.html', **templateData)

################################################################################
# Socket configuration
################################################################################

@socketio.on('connect')
def connect():
    emit('my response', {'data': 'Connected'})
    i=0
    while i<10:
        socketio.emit('daten', i)
        time.sleep(0.01)
        i=i+1

@socketio.on('disconnect')
def disconnect():
    print('Client disconnected')

@socketio.on('my_ping')
def ping_pong():
    emit('my_pong')

@socketio.on('my_event')
def test_message(message):
    emit('my_response',
         {'data': message['data']})

@socketio.on('start_measurement')
def message_1(msg):
    emit('modechange', 'start')
    print('Start Messung')
    start(msg)

@socketio.on('stop_measurement')
def message(msg):
    emit('modechange', 'stop')
    print(msg)

################################################################################
# DB Reading
################################################################################
#verbindung=connection.verbindung()
period = 1     # anzuzeigendes Zeitfenster [s]

def createDbEntry(id, verbindung):
    show.debug('Create DB Entry')
    show.info(id)
    Data=shelve.open('./temp/parameter')
    now=datetime.datetime.now()
    timeString = now.strftime("%d.%m.%Y")
    Data['MessungID']=id
    dat = { 'Bezeichnung': 'deine m',
            'Datum': timeString,
            'ID': id}
    string="INSERT INTO tblMessung('ID', 'Datum', 'Bezeichnung') Values(%d,\'%s\', \'%s\');" %(dat['ID'], dat['Datum'],dat['Bezeichnung'])
    show.debug('Messung angelegt: '+string)
    datensatz=verbindung.insert(string)
    show.debug('Messung gestartet [./apps/werte_schreiben.py]')
    process=Popen(['python', 'apps/werte_schreiben.py'], cwd='.' )
    # process.stdin.write(int(dat['ID']).to_bytes(4, byteorder='big'))
    # process.stdin.close()
    Data.close()

def collect(id,verbindung, period=100, ):
    show.debug('started: Collect')
    show.info('MessungID: %i' %id)
    verbindung=connection.verbindung()
    data=verbindung.abfrage("SELECT MAX(TimeStamp) FROM tblWerte Where MessungID = %i;" %id)
    show.info('data:  '+ str(tuple(data[0])))
    t_max=data[0]['MAX(TimeStamp)']
    t_start= t_max-period
    data=verbindung.abfrage("SELECT TimeStamp, Distanz FROM tblWerte WHERE MessungID = %i AND TimeStamp > %f ;" %(id, t_start))
    t=[]
    dist=[]
    for value in data:
        t.append(list(value)[0])
        dist.append(list(value)[1])
        #print(t , dist)
    return [t, dist]

def start(id):
    verbindung=connection.verbindung()
    createDbEntry(id, verbindung)
    show.debug('Start Messung')
    time.sleep(0.2)
    while True:
        t1=time.time()
        dataset=collect(id, verbindung,period=1.0)
        #show.info('dataset:' + str(tuple(dataset)))
        socketio.emit('measure_data', dataset)
        show.info('emited')
        t_elapsed=time.time()-t1
        show.debug("elapsed:"+str(t_elapsed)+"\n \n")
        time.sleep(0.1)

################################################################################
# Main
################################################################################

if __name__== "__main__":
    socketio.run(app, debug=False)
