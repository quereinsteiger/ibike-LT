import time
import random

def log_time(function):
    def wrapper(*args):
        t0=time.time()
        function(*args)
        t=time.time()-t0
        print(function.__name__ + ": " + str(t))
    return wrapper

@log_time
def random_sort(n):
    return sorted([random.random() for i in range(n)])

@log_time
def count(start,stop):
    i=start
    while i<stop:
        print(i)
        time.sleep(0.001)
        i+=1

if __name__ == "__main__":
 random_sort(1500000)
 count(10,20)
