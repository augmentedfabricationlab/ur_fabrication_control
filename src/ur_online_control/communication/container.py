'''
Created on 11.10.2017

@author: rustr
'''

from threading import Lock
from multiprocessing import Queue
import time
from collections import deque

class Container:

    def __init__(self):
        self.storage = {}
        self.lock = Lock()

    def put(self, key, value = None):
        self.lock.acquire()
        if key in self.storage:
            if type(self.storage[key]) == type({}):
                self.storage[key].update(value)
            else:
                self.storage.update({key: value})
        else:
            self.storage.update({key: value})
        self.lock.release()

    def get(self, key):
        self.lock.acquire()
        value = self.storage[key]
        self.lock.release()
        return value

    def keys(self):
        self.lock.acquire()
        keys = self.storage.keys()
        self.lock.release()
        return keys

    def __repr__(self):
        return str(self.storage)


RCV_QUEUES = Container()
SND_QUEUE = Container()
CONNECTED_CLIENTS = Container()
