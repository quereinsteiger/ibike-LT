import sqlite3 as sql
import time

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
        print('abfrage')
        cursor=self.cur.execute(befehl)
        print('next')
        value=cursor.fetchall()
        print(type(value[0]))
        print('close')
        return value

    def insert(self, befehl):
        self.cur.execute(befehl)
        self.conn.commit()
        return
