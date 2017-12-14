#import numpy as np
from apps import connection
#import matplotlib.pyplot as plt

verbindung=connection.verbindung()

MessungID = 4   # ID der auszulesenden Messung
period = 1     # anzuzeigendes Zeitfenster [s]

data=verbindung.abfrage("SELECT MAX(TimeStamp) FROM tblWerte Where MessungID = %i;" %MessungID)
print(dict(data[0]))
t_max=data[0]['MAX(TimeStamp)']
print(t_max)


t_window= t_max-period
data=verbindung.abfrage("SELECT TimeStamp, Distanz FROM tblWerte WHERE MessungID = %i AND TimeStamp > %f ;" %(MessungID, t_window))
t=[]
dist=[]
for value in data:
    t.append(list(value)[0])
    dist.append(list(value)[1])
print(t , dist)
#plt.plot(t,dist)
#plt.show()
