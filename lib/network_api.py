from abc import abstractmethod, ABCMeta
from queue import Queue, Empty
from selectors import EVENT_READ
from socket import socket, AF_UNIX, AF_INET, SOCK_STREAM
from threading import Thread, Lock
import pickle
from time import sleep
from lib.observable import Observable
from lib.sync_selector import SyncSelector

__author__ = 'alt_mulig'

COM_KILOWATT = 0b00000001
COM_RELAY    = 0b00000010
COM_LOGIN    = 0b00000100

STA_UPDATE = 0b00000001
STA_RELOAD = 0b00000010
STA_USER   = 0b00000100
STA_COOKIE = 0b00001000


class NetworkAPI:
    __metaclass__ = ABCMeta

    observe_start = Observable()
    observe_stop = Observable()

    __send_queue = Queue()
    __send_running = False
    __send_thread = None

    __recv_queue = Queue()
    __recv_running = False
    __recv_thread = None

    __selector = None
    __selector_queue = Queue()
    __selector_running = False
    __selector_thread = None
    __selector_lock = Lock()

    __reconnect_running = False

    _family = None
    _address = None
    _socket = None

    def __init_socket(self, family, address):
        self._family = family
        if family == AF_UNIX:
            if isinstance(address, str):
                self._address = address
            else:
                raise TypeError('Then AF_UNIX, address must be a path (String)')
        elif family == AF_INET:
            if len(address) == 2:
                self._address = address
            else:
                raise TypeError('Then AF_INET, address must be a tuple (IP/HOST, PORT)')
        else:
            raise TypeError('family is either AF_UNIT or AF_INET')

        self._socket = socket(family=self._family, type=SOCK_STREAM)
        # self._socket.setblocking(False)

    def start(self, family, address):
        if not self.__reconnect_running:
            self.__init_socket(family, address)

            if self._setup():
                self.__selector_setup()
                self.__recv_setup()
                self.__send_setup()
                self.__reconnect_running = True
                self.observe_start.update_observers()

    def __selector_setup(self):
        self.__selector = SyncSelector()
        callobj = self._selector_handler(self.__selector)
        self.__selector.register(self._socket, EVENT_READ, callobj)
        self.__selector_running = True
        self.__selector_thread = Thread(name='NetworkAPI.__selector_run()', target=self.__selector_run)
        self.__selector_thread.start()

    @abstractmethod
    def _selector_handler(self, selector):
        pass

    def __selector_run(self):
        while self.__selector_running:
            events = self.__selector.select(timeout=1)
            try:
                for key, mask in events:
                    if key.data is not None:
                        key.data(key.fileobj)
                    else:
                        data_raw = key.fileobj.recv(4096)  # key.fileobj is a object of the class Socket
                        if data_raw is not None:
                            package = pickle.loads(data_raw)
                            self.__recv_queue.put((package, key.fileobj))

            except BaseException as e:
                self._exception_handler(key.fileobj, e)

    def __selector_teardown(self):
        self.__selector_running = False
        self.__selector.unregister(self._socket)
        self.__selector.close()

    def __recv_setup(self):
        self.__recv_running = True
        self.__recv_thread = Thread(name="NetworkAPI.__recv_run()", target=self.__recv_run)
        self.__recv_thread.start()

    def __recv_run(self):
        while self.__recv_running:
            try:
                package, conn = self.__recv_queue.get(True, 0.1)
                self._receive(package, conn)
            except Empty:
                pass

    def __recv_teardown(self):
        self.__recv_running = False

    def __send_setup(self):
        self.__send_running = True
        self.__send_thread = Thread(name="NetworkAPI.__send_run()", target=self.__send_run)
        self.__send_thread.start()

    def __send_run(self):
        while self.__send_running:
            try:
                package, conn = self.__send_queue.get(True, 0.1)
                data_raw = pickle.dumps(package)
                conn.send(data_raw)

                # TODO: Find out if sleep is still necessary
                sleep(0.01)
            except Empty:
                pass
            except BrokenPipeError as e:
                conn.close()
            except OSError as e:
                conn.close()

    def _send(self, package, conn):
        self.__send_queue.put((package, conn))

    def __send_teardown(self):
        self.__send_running = False

    def stop(self):
        if self.__reconnect_running:
            self.__selector_teardown()
            self.__recv_teardown()
            self.__send_teardown()

            self._socket.close()
            self.__reconnect_running = False
            self._teardown()
            self.observe_stop.update_observers()

    def wait(self):
        self.__selector_thread.join()
        self.__recv_thread.join()
        self.__send_thread.join()

    @abstractmethod
    def _setup(self):
        pass

    @abstractmethod
    def _teardown(self):
        pass

    @abstractmethod
    def _receive(self, package, conn):
        pass

    @abstractmethod
    def _exception_handler(self, conn, exception):
        raise NotImplementedError('The _exception_handler method is not defined in the inherited class')
