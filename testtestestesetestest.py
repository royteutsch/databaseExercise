import random

import database_locker
import threading
import time


def read_worker(key, num):
    for i in range(1000):
        print(d.get_value(key=key))
        print(num)


def write_worker(key):
    for i in range(1000):
        d.set_value(key=key, val=str(i))
        print("Wrote " + str(i) +" to key " + key + " at time " + str(time.time()))

def worker(key):
    time.sleep(random.random())

d = database_locker.DatabaseLocker("dbText.txt")
threads_1 = []
for index in range(3):
    x = threading.Thread(target=write_worker, args=('hello', ))
    threads_1.append(x)


threads_2 = []
for index in range(10):
    x = threading.Thread(target=read_worker, args=('hello', index, ))
    threads_2.append(x)
for t in threads_1:
    t.start()
for t in threads_2:
    t.start()

print(d.data)