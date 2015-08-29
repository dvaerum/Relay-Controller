from abc import abstractmethod, ABCMeta
from selectors import DefaultSelector, EVENT_READ
from socket import socket, AF_UNIX, AF_INET, SOCK_STREAM
from threading import Thread
from lib.observable import Observable

__author__ = 'alt_mulig'

COM_KILOWATT = 0b00000001
COM_RELAY = 0b00000010

STA_UPDATE = 0b00000001
STA_RELOAD = 0b00000010


class NetworkAPI(object):
    __metaclass__ = ABCMeta

    observe_start = Observable()
    observe_stop = Observable()

    _running = False
    _thread = None
    _socket = None

    _family = None
    _socket_file = None
    _host = None
    _port = None

    def __init__(self, family, address):
        self._family = family
        if family == AF_UNIX:
            self._socket_file = address
        elif family == AF_INET:
            if len(address) == 2:
                self._host = address[0]
                self._port = address[1]
            else:
                raise TypeError('Then AF_INET address is a tuple (IP/HOST, PORT)')
        else:
            raise TypeError('family is either AF_UNIT or AF_INET')

    def start(self):
        if not self._running:
            # self._socket = socket(family=AF_UNIX, type=SOCK_STREAM)
            self._socket = socket(family=self._family, type=SOCK_STREAM)
            # self._socket.setblocking(False)

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
