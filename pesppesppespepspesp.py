import random
import database_locker
import time
from multiprocessing import freeze_support
from multiprocessing import Process


def read_worker(key, d):
    for i in range(1000):
        freeze_support()
        val = d.get_value(key=key)
        print(key + " corresponds to " + val)


def write_worker(key, d):
    for i in range(10000):
        freeze_support()
        d.set_value(key=key, val=str(i))
        print("Wrote " + str(i) + " to key " + key + " at time " + str(time.time()))
        print("Number: " + str(d.number))


def worker():
    time.sleep(random.random())


if __name__ == '__main__':
    freeze_support()
    da = database_locker.DatabaseLocker("dbText.txt", "T")
    freeze_support()
    threads_1 = []
    for index in range(10):
        freeze_support()
        x = Process(target=write_worker, args=('hello', da,))
        threads_1.append(x)

    threads_2 = []
    for index in range(100):
        freeze_support()
        x = Process(target=read_worker, args=('hello', da,))
        threads_2.append(x)

    print("starting...")
    for t in threads_1:
        freeze_support()
        t.start()
    for t in threads_2:
        freeze_support()
        t.start()

    print(da.data)
    print(da.number)
