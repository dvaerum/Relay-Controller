from abc import abstractmethod, ABCMeta
from selectors import DefaultSelector, EVENT_READ
from socket import socket, AF_UNIX, SOCK_STREAM
from threading import Thread
from lib.observable import Observable

__author__ = 'alt_mulig'

COM_KILOWATT =  0b00000001

STA_UPDATE =    0b00000001
STA_STATUS =    0b00000010


class NetworkAPI(object):
    __metaclass__ = ABCMeta

    observe_start = Observable()
    observe_stop = Observable()

    _socket = None
    _running = False
    _thread = None

    def __init__(self, socket_file: str):
        self.socket_file = socket_file

    def start(self):
        if not self._running:
            self._socket = socket(family=AF_UNIX, type=SOCK_STREAM)
            self._socket.setblocking(False)

            if self._setup():
                self._selector = DefaultSelector()
                self._selector.register(self._socket, EVENT_READ, self._receive)

                self._running = True
                self._thread = Thread(name="ServerAPI.__run()", target=self.__run)
                self._thread.start()
                self.observe_start.update_observers()

    def stop(self):
        if self._running:
            self._running = False
            self._socket.close()
            self._teardown()
            self._selector.unregister(self._socket)
            self._selector.close()
            self.observe_stop.update_observers()

    def __run(self):
        while self._running:
            events = self._selector.select(timeout=1)
            for key, mask in events:
                callback = key.data
                callback(key.fileobj)

    @abstractmethod
    def _setup(self):
        pass

    @abstractmethod
    def _teardown(self):
        pass

    @abstractmethod
    def _receive(self, sock: socket):
        pass
