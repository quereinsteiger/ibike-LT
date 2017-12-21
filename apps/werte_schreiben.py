import shelve
from random import random
import time
import logging
# from apps
import connection

#logging.config.fileConfig('../config/logging.conf')
logfile=logging.getLogger('logfile')
show=logging.getLogger('show')

def distanz():
    logging.info('Aufruf Distanz')
    value=[time.time(),random()]
    return value

def dist_schreiben(MessungID):

    verbindung = connection.verbindung()
    werte=distanz()

    string="INSERT INTO tblWerte('MessungID','TimeStamp','Distanz') Values(%d,%f,%f);" %(MessungID, werte[0], werte[1])
    show.info('START Wert schreiben')
    show.debug(string)
    start=time.time()
    verbindung.insert(string)
    elapsed=time.time()-start
    show.info('ENDE Wert schreiben | Dauer des Schreibvorgangs: %f' %(elapsed))
    return

if __name__=="__main__":
    MessungID=shelve.open('./temp/parameter')
    ID=int(MessungID['MessungID'])
    MessungID.close()
    i=0
    while i<50:
        dist_schreiben(ID)
        time.sleep(0.1)
        i=i+1
