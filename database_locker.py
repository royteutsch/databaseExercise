import os
import time
import pickle
from typing import Optional

import database_writer
import threading
from threading import Semaphore

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


class DatabaseLocker(database_writer.DatabaseWriter):
    _rLock_sema = MySemaphore(10)

    def __init__(self, file_location: str):
        super().__init__(file_location)
        self.wLock = threading.Lock()
        self.aquireLock = threading.Lock()
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
            DatabaseLocker.current_mode = "W"
            super().set_value(key, val)
        finally:
            DatabaseLocker.current_mode = "N"
            self.wLock.release()

    def get_value(self, key):  # Reading Privilege
        with self.aquireLock:
            DatabaseLocker._rLock_sema.acquire()
            while self.wLock.locked():
                time.sleep(0.0001)
        try:
            DatabaseLocker.current_mode = "R"
            return super().get_value(key)
        finally:
            DatabaseLocker.current_mode = "N"
            DatabaseLocker._rLock_sema.release()

    def delete_value(self, key):  # Writing Privilege
        with self.aquireLock:
            self.wLock.acquire()
            while DatabaseLocker._rLock_sema.counter > 0:
                time.sleep(0.0001)
        try:
            DatabaseLocker.current_mode = "W"
            val = super().delete_value(key)
            return val
        finally:
            DatabaseLocker.current_mode = "N"
            self.wLock.release()

