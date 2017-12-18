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
import time

################################################################################
# Global Configs
################################################################################

async_mode = None

app=Flask(__name__)
logging.basicConfig(filename='brain.log', level=logging.INFO, format='%(asctime)s %(message)s')

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
verbindung=connection.verbindung()
period = 1     # anzuzeigendes Zeitfenster [s]

def createDbEntry(id):
    print('Create DB Entry')
    print(id)
    Data=shelve.open('./temp/parameter')
    print('opened')
    now=datetime.datetime.now()
    timeString = now.strftime("%d.%m.%Y")
    Data['MessungID']=id
    dat = { 'Bezeichnung': 'deine m',
            'Datum': timeString,
            'ID': id}
    string="INSERT INTO tblMessung('ID', 'Datum', 'Bezeichnung') Values(%d,\'%s\', \'%s\');" %(dat['ID'], dat['Datum'],dat['Bezeichnung'])
    logging.info('Messung angelegt: '+string)
    print(string)
    verbindung=connection.verbindung()
    datensatz=verbindung.insert(string)
    logging.info('Messung gestartet [./apps/werte_schreiben.py]')
    process=Popen(['python', 'apps/werte_schreiben.py'], cwd='.' )
    # process.stdin.write(int(dat['ID']).to_bytes(4, byteorder='big'))
    # process.stdin.close()
    Data.close()

def collect(id, period=100):
    print('Collect')
    print(id)
    data=verbindung.abfrage("SELECT MAX(TimeStamp) FROM tblWerte Where MessungID = %i;" %id)
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
    createDbEntry(id)
    print('Start Messung')
    while True:
        t1=time.time()
        dataset=collect(id, period)
        print(dataset)
        socketio.emit('measure_data', dataset)
        t_elapsed=time.time()-t1
        print("elapsed:"+str(t_elapsed)+"\n \n")
        time.sleep(0.1)

################################################################################
# Main
################################################################################

if __name__== "__main__":
    socketio.run(app, debug=False)