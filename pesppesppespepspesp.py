import random
from multiprocessing import freeze_support

import database_locker
import multiprocessing as parallel
import time


def read_worker(key):
    for i in range(1000):
        freeze_support()
        val = d.get_value(key=key)
        print(key + " corresponds to " + val)


def write_worker(key):
    for i in range(10000):
        freeze_support()
        d.set_value(key=key, val=str(i))
        print("Wrote " + str(i) + " to key " + key + " at time " + str(time.time()))
        print("Number: " + str(d.number))


def worker():
    time.sleep(random.random())

freeze_support()
d = database_locker.DatabaseLocker("dbText.txt", "T")
freeze_support()
threads_1 = []
for index in range(2):
    freeze_support()
    x = parallel.Process(target=write_worker, args=('hello',))
    threads_1.append(x)

threads_2 = []
for index in range(2):
    freeze_support()
    x = parallel.Process(target=read_worker, args=('hello', ))
    threads_2.append(x)

print("starting...")
for t in threads_1:
    freeze_support()
    t.start()
for t in threads_2:
    freeze_support()
    t.start()

print(d.data)
print(d.number)
