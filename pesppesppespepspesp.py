import multiprocessing
import random
import database_locker
import time
from multiprocessing import Process
from multiprocessing.synchronize import Semaphore as SemaphoreProcess
from multiprocessing.synchronize import Lock as LockProcess


class MyLock(LockProcess):  # Literally just a lock with the ability to check if its locked

    def __init__(self):
        super(MyLock, self).__init__(ctx=multiprocessing.get_context())

    def locked(self):
        is_locked = super(MyLock, self).acquire(block=False)
        if not is_locked:
            return True
        else:
            super(MyLock, self).release()
            return False


def read_worker(key, d):
    for i in range(1000):
        val = d.get_value(key=key)
        print(key + " corresponds to " + val)


def write_worker(key, d):
    for i in range(10000):
        d.set_value(key=key, val=str(i))
        print("Wrote " + str(i) + " to key " + key + " at time " + str(time.time()))
        print("Number: " + str(d.number))


def worker():
    time.sleep(random.random())


if __name__ == '__main__':
    plock = multiprocessing.Lock()
    pmlock = MyLock()
    da = database_locker.DatabaseLocker(file_location="dbText.txt", mode="T", lock1=pmlock, lock2=plock)
    threads_1 = []
    for index in range(10):
        x = Process(target=write_worker, args=('hello', da,))
        threads_1.append(x)

    threads_2 = []
    for index in range(100):
        x = Process(target=read_worker, args=('hello', da,))
        threads_2.append(x)

    print("starting...")
    for t in threads_1:
        t.start()
    for t in threads_2:
        t.start()

    print(da.data)
    print(da.number)
