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

@app.route('/test')
def run():

    Popen(['python', './apps/test2.py'], stdout = PIPE )
    return render_template('test.html')

@app.route('/run/<par1>/',methods=['POST', 'GET'])
def laeuft(par1):

    if request.method=='POST':
            Data=shelve.open('./temp/parameter')
            now=datetime.datetime.now()
            timeString = now.strftime("%d.%m.%Y")
            Data['MessungID']=par1
            dat = { 'Bezeichnung': request.form['Bezeichnung'],
                    'Datum': timeString,
                    'ID': int(par1)}
            string="INSERT INTO tblMessung('ID', 'Datum', 'Bezeichnung') Values(%d,\'%s\', \'%s\');" %(dat['ID'], dat['Datum'],dat['Bezeichnung'])
            logging.info('Messung angelegt: '+string)
            print(string)
            verbindung=connection.verbindung()
            datensatz=verbindung.insert(string )
            logging.info('Messung gestartet [./apps/werte_schreiben.py]')
            process=Popen(['python', 'apps/werte_schreiben.py'], cwd='.' )
            # process.stdin.write(int(dat['ID']).to_bytes(4, byteorder='big'))
            # process.stdin.close()
            Data.close()
            return render_template('run.html', **dat)
    else:
        return redirect('./')

################################################################################
# Socket configuration
################################################################################

@socketio.on('connect')
def test_connect():
    emit('my response', {'data': 'Connected'})

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

@socketio.on('my_ping')
def ping_pong():
    emit('my_pong')

@socketio.on('my_event')
def test_message(message):
    emit('my_response',
         {'data': message['data']})

################################################################################
# Main
################################################################################

if __name__== "__main__":
    socketio.run(app, debug=True)