import os
import time
import pickle
from typing import Optional
import database_writer
import threading
from threading import Semaphore
import multiprocessing
from multiprocessing import Semaphore as SemaphoreProcess
from multiprocessing import Lock as LockProcess


class MyLock(LockProcess):  # Literally just a lock with the ability to check if its locked
    
    def __init__(self):
        super(MyLock, self).__init__()
    
    def locked(self):
        is_locked = super(MyLock, self).acquire(block=False)
        if not is_locked:
            return True
        else:
            super(MyLock, self).release()
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
        super(MySemaphoreProcess, self).__init__(maxcount)

    def acquire(self):
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

    def __init__(self, file_location: str, mode: str):
        super().__init__(file_location)
        if mode == "T":  # Thread mode
            self.wLock = threading.Lock()
            self.aquireLock = threading.Lock()
        else:  # Process mode
            self.wLock = MyLock()
            self.aquireLock = multiprocessing.Lock()
        self.number = 0
        if os.path.getsize(self.file_loc) != 0:  # This means that the file is not empty
            db_file = open(self.file_loc, 'rb')
            self.data = pickle.load(db_file)
            db_file.close()

    def set_value(self, key, val):  # Writing Privilege
        with self.aquireLock:
            self.wLock.acquire()
            while DatabaseLocker._rLock_sema.counter > 0:
                time.sleep(0.0001)
        try:
            super().set_value(key, val)
        finally:
            self.number += 10
            self.wLock.release()

    def get_value(self, key):  # Reading Privilege
        with self.aquireLock:
            DatabaseLocker._rLock_sema.acquire()
            while self.wLock.locked():
                time.sleep(0.0001)
        try:
            return super().get_value(key)
        finally:
            self.number -= 10
            DatabaseLocker._rLock_sema.release()

    def delete_value(self, key):  # Writing Privilege
        with self.aquireLock:
            self.wLock.acquire()
            while DatabaseLocker._rLock_sema.counter > 0:
                time.sleep(0.0001)
        try:
            val = super().delete_value(key)
            return val
        finally:
            self.number += 10
            self.wLock.release()

