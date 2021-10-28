import os
import pickle
import database_writer
import threading
from threading import Semaphore


class DatabaseLocker(database_writer.DatabaseWriter):
    _rLock_sema = Semaphore(10)
    current_mode = "N"

    def __init__(self, file_location: str):
        super().__init__(file_location)
        self.wLock = threading.Lock()
        if os.path.getsize(self.file_loc) != 0:  # This means that the file is not empty
            db_file = open(self.file_loc, 'rb')
            self.data = pickle.load(db_file)
            db_file.close()

    def set_value(self, key, val):  # Writing Privilage
        while DatabaseLocker.current_mode == "R":
            pass
        self.wLock.acquire()
        try:
            DatabaseLocker.current_mode = "W"
            super().set_value(key, val)
        finally:
            DatabaseLocker.current_mode = "N"
            self.wLock.release()

    def get_value(self, key):  # Reading Privilage
        while DatabaseLocker.current_mode == "W":
            pass
        DatabaseLocker._rLock_sema.acquire()
        try:
            DatabaseLocker.current_mode = "R"
            return super().get_value(key)
        finally:
            DatabaseLocker.current_mode = "N"
            DatabaseLocker._rLock_sema.release()

    def delete_value(self, key):  # Writing Privilage
        while DatabaseLocker.current_mode == "R":
            pass
        self.wLock.acquire()
        try:
            DatabaseLocker.current_mode = "W"
            val = super().delete_value(key)
            return val
        finally:
            DatabaseLocker.current_mode = "N"
            self.wLock.release()

