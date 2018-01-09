import sqlite3 as sql
import time
import logging

logfile=logging.getLogger('logfile')
show=logging.getLogger('show')

class verbindung():
    """Verbindung zur Datenbank herstellen"""
    dbfile= "./Data/ibike.sqlite"

    def __init__(self, datenbank=None, foreign_keys=False):
        self.datenbank = datenbank if datenbank else verbindung.dbfile
        self.conn = sql.connect(self.datenbank)
        self.conn.row_factory=sql.Row
        self.cur = self.conn.cursor()

        if foreign_keys:
            self.cur.execute('Pragma foreign_keys = ON;')

    def abfrage(self, befehl):
        show.debug('Abfrage: '+ befehl)
        cursor=self.cur.execute(befehl)
        value=cursor.fetchall()
        #show.debug('Abfrage return:'+(str(value)))
        return value

    def insert(self, befehl):
        show.debug('Insert: ' + befehl)
        self.cur.execute(befehl)
        self.conn.commit()
        return
