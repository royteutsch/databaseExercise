import ctypes
import os
import time
import pickle
from typing import Optional
import database_writer
from threading import Semaphore
import multiprocessing
from multiprocessing.synchronize import Semaphore as SemaphoreProcess
from multiprocessing.synchronize import Lock as LockProcess


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
        self.counter += 1
        super(MySemaphore, self).acquire()

    def release(self, n: int = ...) -> None:
        self.counter -= 1
        super(MySemaphore, self).release()

    def isFullyLocked(self):
        return self.counter == self.maxcount


class MySemaphoreProcess(SemaphoreProcess):
    def __init__(self, maxcount):
        self.MyCounter = 0
        self.MyCounter = multiprocessing.Value('i', 0)
        self.maxcount = maxcount
        super(MySemaphoreProcess, self).__init__(maxcount, ctx=multiprocessing.get_context())

    def acquire(self, block: bool = ..., timeout: Optional[float] = ...) -> bool:
        self.MyCounter.value += 1
        print(f"SemaphoreProcess: {os.getpid()} internal counter raised to {self.MyCounter.value}")
        super(MySemaphoreProcess, self).acquire()

    def release(self) -> None:
        self.MyCounter.value -= 1
        print(f"SemaphoreProcess: {os.getpid()} internal counter reduced to {self.MyCounter.value}")
        super(MySemaphoreProcess, self).release()

    def isFullyLocked(self):
        return self.MyCounter.value == self.maxcount

    def __str__(self):
        return str(self.MyCounter)



class DatabaseLocker(database_writer.DatabaseWriter):
    _rLock_semaThread = MySemaphore(10)

    def __init__(self, file_location: str, mode: str, lock1, lock2, count, locky):
        super().__init__(file_location)
        self.number = multiprocessing.Value('i', 0)
        self.mode = mode
        self.count = count
        self.lock = locky
        if mode == "T":  # Thread mode
            self.wLock = lock1  # threading.Lock()
            self.aquireLock = lock2  # threading.Lock()
        else:  # Process mode
            self.rLock_semaProcess = MySemaphoreProcess(10)
            self.wLock = lock1  # MyLock()
            self.aquireLock = lock2  # multiprocessing.Lock()
            print("DatabaseLocker-------------semaphore created")
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
            while DatabaseLocker._rLock_semaThread.counter > 0:
                    print("Set Value is Waiting")
                    time.sleep(0.0001)
            self.aquireLock.release()
            print("Releasing acquire lock for set")
        else:
            self.aquireLock.acquire()
            print(f"DatabaseLocker.set_value:{os.getpid()} Acquiring set")
            self.wLock.acquire()
            print(self.rLock_semaProcess)
            while self.rLock_semaProcess.MyCounter.value > 0:
                print(f"DatabaseLocker.set_value:{os.getpid()} Set Value  is Waiting")
                time.sleep(0.0001)
            self.aquireLock.release()
            print(f"DatabaseLocker.set_value:{os.getpid()} Releasing acquire lock for set")
            # cant_write = True
            # while cant_write:
            #     if self.count.value == 0:
            #         print(f"DatabaseLocker.set_value:{os.getpid()} Acquiring set")
            #         self.aquireLock.acquire()
            #         print(f"DatabaseLocker.set_value:{os.getpid()} Acquire lock acquired for set")
            #         self.wLock.acquire()
            #         print(f"DatabaseLocker.set_value:{os.getpid()} Writing lock acquired for set")
            #         if self.count.value == 0:
            #             with self.lock:
            #                 self.count.value = -1
            #                 print(f"DatabaseLocker.set_value:{os.getpid()} count SET TO {self.count.value}")
            #         self.aquireLock.release()
            #         print(f"DatabaseLocker.set_value:{os.getpid()} Releasing acquire lock for set")
            #     else:
            #         print(f"DatabaseLocker.set_value:{os.getpid()} Set Value  is Waiting")
            #         time.sleep(0.0001)
            #         continue

            #     if self.count.value == -1:
            #         cant_write = False
            #     time.sleep(0.0001)
        try:
            super().set_value(key, val)
        finally:
            if self.mode == "T":
                print(f"DatabaseLocker.set_value:{os.getpid()} finishing write")
                self.wLock.release()
            else:
                print(f"DatabaseLocker.set_value:{os.getpid()} finishing write")
                self.wLock.release()
                # print(f"DatabaseLocker.set_value:{os.getpid()} finishing write")
                # with self.lock:
                #     print(f"DatabaseLocker.set_value:{os.getpid()} Counter restarted")
                #     self.count.value = 0
                # if self.wLock.locked():
                #     self.wLock.release()
                #     time.sleep(0.0001)
            self.number.value += 10

    def get_value(self, key):  # Reading Privilege
        if self.mode == "T":
            self.aquireLock.acquire()
            print("Acquiring get")
            DatabaseLocker._rLock_semaThread.acquire()
            while self.wLock.locked():
                print("Get Value is Waiting")
                time.sleep(0.0001)
            self.aquireLock.release()
            print("Releasing acquire lock for get")
        else:
            self.aquireLock.acquire()
            print(f"DatabaseLocker.get_value:{os.getpid()} Acquiring get")
            self.rLock_semaProcess.acquire()
            while self.wLock.locked():
                print(f"DatabaseLocker.get_value:{os.getpid()} Waiting")
                time.sleep(0.0001)
            self.aquireLock.release()
            print(f"DatabaseLocker.get_value:{os.getpid()} Releasing acquire lock for get")
            # success = False
            # while not success:
            #     if 10 > self.count.value >= 0:
            #         print(f"DatabaseLocker.get_value:{os.getpid()} Acquiring get")
            #         self.aquireLock.acquire()
            #         print(f"DatabaseLocker.get_value:{os.getpid()} Acquire lock initiated for read")
            #         if 10 > self.count.value >= 0:
            #             with self.lock:
            #                 self.count.value += 1
            #             success = True
            #             print(f"DatabaseLocker.get_value:{os.getpid()} count SET TO {self.count.value}")
            #         self.aquireLock.release()
            #         print(f"DatabaseLocker.get_value:{os.getpid()} Releasing acquire lock for get")
            #     else:
            #         print(f"DatabaseLocker.get_value:{os.getpid()} Waiting")
        try:
            return super().get_value(key)
        finally:
            with self.number.get_lock():
                self.number.value -= 10
            if self.mode == "T":
                DatabaseLocker._rLock_semaThread.release()
            else:
                # self.aquireLock.acquire()
                # with self.lock:
                #     self.count.value -= 1
                #     print(f"DatabaseLocker.get_value:{os.getpid()} count REDUCED TO {self.count.value}")
                self.rLock_semaProcess.release()
                # self.aquireLock.release()

    def delete_value(self, key):  # Writing Privilege
        if self.mode == "T":
            self.aquireLock.acquire()
            print("Acquiring del")
            self.wLock.acquire()
            while DatabaseLocker._rLock_semaThread.counter > 0:
                print("Del Value is Waiting")
                time.sleep(0.0001)
            self.aquireLock.release()
            print("Releasing acquire lock for del")
        else:
            while self.count >= 0:
                if self.count == 0:
                    print("DatabaseLocker.delete_value: Acquiring del")
                    self.aquireLock.acquire()
                    self.wLock.acquire()
                    if self.count == 0:
                        with self.lock:
                            self.count.value = -1
                            print(f"DatabaseLocker.delete_value: count SET TO {self.count.value}")
                    self.aquireLock.release()
                    print("DatabaseLocker.delete_value: Releasing acquire lock for del")
                else:
                    print("DatabaseLocker.delete_value: Del Value is Waiting")
                time.sleep(0.0001)
        try:
            val = super().delete_value(key)
            return val
        finally:
            self.aquireLock.acquire()
            self.wLock.release()
            with self.lock:
                self.count.value = 0
            self.aquireLock.release()
            self.number += 10

