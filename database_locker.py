import os
import time
import pickle
from typing import Optional
import database_writer
from threading import Semaphore
import multiprocessing
from multiprocessing.synchronize import Semaphore as SemaphoreProcess
from multiprocessing.synchronize import Lock as LockProcess
import multiprocessing.queues


class MyLock(LockProcess):  # Literally just a lock with the ability to check if its locked

    def __init__(self):
        super(MyLock, self).__init__(ctx=multiprocessing.get_context())

    def locked(self):
        is_locked = super().acquire(block=False)
        if not is_locked:
            return True
        else:
            super().release()
            return False


class MySemaphore(Semaphore):
    def __init__(self, maxcount):
        self.counter = 0
        self.maxcount = maxcount
        super(MySemaphore, self).__init__(maxcount)

    def acquire(self, blocking: bool = ..., timeout: Optional[float] = ...) -> bool:
        super(MySemaphore, self).acquire()
        self.counter += 1

    def release(self, n: int = ...) -> None:
        self.counter -= 1
        super(MySemaphore, self).release()

    def isFullyLocked(self):
        return self.counter == self.maxcount


class MySemaphoreProcess(SemaphoreProcess):
    def __init__(self, maxcount):
        self.counter = 0
        self.maxcount = maxcount
        super(MySemaphoreProcess, self).__init__(maxcount, ctx=multiprocessing.get_context())

    def acquire(self, block: bool = ..., timeout: Optional[float] = ...) -> bool:
        super(MySemaphoreProcess, self).acquire()
        self.counter += 1

    def release(self) -> None:
        self.counter -= 1
        super(MySemaphoreProcess, self).release()

    def isFullyLocked(self):
        return self.counter == self.maxcount


class DatabaseLocker(database_writer.DatabaseWriter):
    _rLock_sema = MySemaphore(10)
    _rLock_semaProcess = MySemaphoreProcess(10)
    number = 0
    counter = 0

    def __init__(self, file_location: str, mode: str, lock1, lock2):
        super().__init__(file_location)
        self.mode = mode
        self.queueue = multiprocessing.queues.Queue
        if mode == "T":  # Thread mode
            self.wLock = lock1  # threading.Lock()
            self.aquireLock = lock2  # threading.Lock()
        else:  # Process mode
            self.wLock = lock1  # MyLock()
            self.aquireLock = lock2  # multiprocessing.Lock()
        if os.path.getsize(self.file_loc) != 0:  # This means that the file is not empty
            db_file = open(self.file_loc, 'rb')
            self.data = pickle.load(db_file)
            print(self.data)
            db_file.close()

    def set_value(self, key, val):  # Writing Privilege
        if self.mode == "T":
            self.aquireLock.acquire()
            print("Acquiring set")
            self.wLock.acquire()
            while DatabaseLocker._rLock_sema.counter > 0:
                    print("Set Value is Waiting")
                    time.sleep(0.0001)
            self.aquireLock.release()
            print("Releasing acquire lock for set")
        else:
            while DatabaseLocker.counter >= 0:
                if DatabaseLocker.counter == 0:
                    self.aquireLock.acquire()
                    self.wLock.acquire()
                    if DatabaseLocker.counter == 0:
                        DatabaseLocker.counter = -1
                    self.aquireLock.release()
                time.sleep(0.0001)
        try:
            super().set_value(key, val)
        finally:
            self.aquireLock.acquire()
            self.wLock.release()
            DatabaseLocker.counter = 0
            self.aquireLock.release()
            DatabaseLocker.number += 10

    def get_value(self, key):  # Reading Privilege
        if self.mode == "T":
            self.aquireLock.acquire()
            print("Acquiring get")
            DatabaseLocker._rLock_sema.acquire()
            while self.wLock.locked():
                print("Get Value is Waiting")
                time.sleep(0.0001)
            self.aquireLock.release()
            print("Releasing acquire lock for get")
        else:
            success = False
            while not success:
                if 10 > DatabaseLocker.counter >= 0:
                    self.aquireLock.acquire()
                    if 10 > DatabaseLocker.counter >= 0:
                        DatabaseLocker.counter += 1
                        success = True
                    self.aquireLock.release()
        try:
            return super().get_value(key)
        finally:
            DatabaseLocker.number -= 10
            if self.mode == "T":
                DatabaseLocker._rLock_sema.release()
            else:
                self.aquireLock.acquire()
                DatabaseLocker.counter -= 1
                self.aquireLock.release()

    def delete_value(self, key):  # Writing Privilege
        if self.mode == "T":
            self.aquireLock.acquire()
            print("Acquiring del")
            self.wLock.acquire()
            while DatabaseLocker._rLock_sema.counter > 0:
                print("Del Value is Waiting")
                time.sleep(0.0001)
            self.aquireLock.release()
            print("Releasing acquire lock for del")
        else:
            while DatabaseLocker.counter >= 0:
                if DatabaseLocker.counter == 0:
                    self.aquireLock.acquire()
                    self.wLock.acquire()
                    if DatabaseLocker.counter == 0:
                        DatabaseLocker.counter = -1
                    self.aquireLock.release()
                time.sleep(0.0001)
        try:
            val = super().delete_value(key)
            return val
        finally:
            self.aquireLock.acquire()
            self.wLock.release()
            DatabaseLocker.counter = 0
            self.aquireLock.release()
            DatabaseLocker.number += 10

