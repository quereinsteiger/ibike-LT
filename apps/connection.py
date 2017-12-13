import sqlite3 as sql
import time

class verbindung():
    """Verbindung zur Datenbank herstellen"""
    def __init__(self, datenbank="./data/ibike.sqlite"):
        self.datenbank = datenbank

    def abfrage(self, befehl):
        con=sql.connect(self.datenbank)
        con.row_factory=zeilen_dict
        cursor=con.cursor()
        cursor.execute(befehl)
        value=cursor.fetchall()
        con.commit()
        con.close()
        return value
    def insert(self, befehl):
        con=sql.connect(self.datenbank)
        cursor=con.cursor()
        cursor.execute(befehl)
        con.commit()
        con.close()
        return

    # def __del__(self):
    #     self.con.close()

def auslesen(id=1):
    a=verbindung()
    ds=a.abfrage("SELECT * FROM tblFahrer WHERE tblFahrer.ID=" + str(id))
    Username = ds['Username']
    Vorname = ds['Vorname']
    Nachname = ds['Nachname']
    Geburtsdatum = ds['Geburtsdatum']
    Geschlecht = ds['Geschlecht']
    Groesse = ds['Groesse']
    Gewicht = ds['Gewicht']
    return fahrer(Username, Vorname, Nachname, Geburtsdatum, Geschlecht, Groesse,Gewicht)




class fahrer():
    def __init__(self, Username, Vorname, Nachname, Geburtsdatum, Geschlecht, Groesse,Gewicht, id=0 ):
        self.__id = id
        self.Username = Username
        self.Vorname = Vorname
        self.Nachname = Nachname
        self.Geburtsdatum = Geburtsdatum
        self.Geschlecht = Geschlecht
        self.Groesse = Groesse
        self.Gewicht = Gewicht

    def alter(self):
        date_of_birth=time.strptime(self.Geburtsdatum, "%d.%m.%Y")
        num_from_birth=time.mktime(date_of_birth)
        age=time.time()-num_from_birth
        return time.localtime(age).tm_year-1970



# Ausgabe der Abfragen als Dictionary
def zeilen_dict(cursor, zeile):
    ergebnis = {}
    for spaltennr, spalte in enumerate(cursor.description):
        ergebnis[spalte[0]] = zeile[spaltennr]
    return ergebnis
