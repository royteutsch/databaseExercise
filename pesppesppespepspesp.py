import multiprocessing
import random
import database_locker
import time
from multiprocessing import Process
from multiprocessing.synchronize import Lock as LockProcess


class MyLock(LockProcess):  # Literally just a lock with the ability to check if its locked

    def __init__(self):
        super(MyLock, self).__init__(ctx=multiprocessing.get_context())

    def locked(self):
        is_locked = self.acquire(block=False)
        if not is_locked:
            return True
        else:
            self.release()
            return False


class TestDatabase:
    def __init__(self, file_location: str, mode: str, lock1: MyLock, lock2: multiprocessing.Lock(), count, locky):
        self.database = database_locker.DatabaseLocker(file_location=file_location, mode=mode, lock1=lock1, lock2=lock2,
                                                       count=count, locky=locky)

    def set_val(self, key, value):
        self.database.set_value(key, value)

    def get_val(self, key):
        return self.database.get_value(key)


def read_worker(key, d):
    val = None
    for i in range(10):
        val = d.get_val(key=key)
        print(key + " corresponds to " + str(val))
        print("Number: " + str(d.database.number.value))
        print(d.database.data)

    print(f"last val = {val}")


def write_worker(key, d):
    for i in range(100):
        d.set_val(key=key, value=str(i))
        print("Wrote " + str(i) + " to key " + key + " at time " + str(time.time()))
        print("Number: " + str(d.database.number.value))
        print(d.database.data)


def worker():
    time.sleep(random.random())


if __name__ == '__main__':
    plock = MyLock()
    pmlock = MyLock()
    v = multiprocessing.Value('i', 0)
    lock = multiprocessing.Lock()
    da = TestDatabase(file_location="dbText.txt", mode="P", lock1=pmlock, lock2=plock, count=v, locky=lock)
    threads_1 = []
    for index in range(10):
        x = Process(target=write_worker, args=("hello", da,))
        threads_1.append(x)

    threads_2 = []
    for index in range(100):
        x = Process(target=read_worker, args=("hello", da,))
        threads_2.append(x)

    print("starting...")
    for t in threads_1:
        t.start()
    for t in threads_2:
        t.start()
