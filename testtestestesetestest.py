import random
import threading
import multiprocessing
import database_locker
import threading as parallel
import time


def read_worker(key):
    for i in range(100):
        val = d.get_value(key=key)
        print(key + " corresponds to " + val)


def write_worker(key):
    for i in range(1000):
        d.set_value(key=key, val=str(i))
        print("Wrote " + str(i) + " to key " + key + " at time " + str(time.time()))
        print("Number: " + str(d.number.value))


def worker():
    time.sleep(random.random())


plock = threading.Lock()
pmlock = threading.Lock()
v = multiprocessing.Value('i', 0)
lock = threading.Lock()
d = database_locker.DatabaseLocker("dbText.txt", "T", plock, pmlock, v, lock)

threads_1 = []
for index in range(10):
    x = parallel.Thread(target=write_worker, args=('hello',))
    threads_1.append(x)

threads_2 = []
for index in range(100):
    x = parallel.Thread(target=read_worker, args=('hello',))
    threads_2.append(x)
for t in threads_1:
    t.start()
for t in threads_2:
    t.start()

print(d.data)
print(d.number)
