#import numpy as np
from apps import connection
import time
#import matplotlib.pyplot as plt            # plot funktinoniert nicht in meiner virtuellen Umgebung -.-

verbindung=connection.verbindung()

MessungID = 6   # ID der auszulesenden Messung
period = 1     # anzuzeigendes Zeitfenster [s]

def collect(MessungID, period=10):
    data=verbindung.abfrage("SELECT MAX(TimeStamp) FROM tblWerte Where MessungID = %i;" %MessungID)
    #print(dict(data[0]))
    t_max=data[0]['MAX(TimeStamp)']
    #print(t_max)


    t_start= t_max-period
    data=verbindung.abfrage("SELECT TimeStamp, Distanz FROM tblWerte WHERE MessungID = %i AND TimeStamp > %f ;" %(MessungID, t_start))
    t=[]
    dist=[]
    for value in data:
        t.append(list(value)[0])
        dist.append(list(value)[1])
        #print(t , dist)
    return [t, dist]

if __name__=="__main__":
    while True:
        t1=time.time()
        print(collect(MessungID, period))
        t_elapsed=time.time()-t1
        print("elapsed:"+str(t_elapsed)+"\n \n")
        time.sleep(0.1)






#plt.plot(t,dist)
#plt.show()
