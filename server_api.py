from os.path import exists
from os import remove
from queue import Queue
from selectors import EVENT_READ
from socket import socket, AF_UNIX
from lib import network_api
from state_machine import state_machine
from watt import watt

__author__ = 'alt_mulig'


class __ServerAPI(network_api.NetworkAPI):

    __connections = []
    __update_queue = Queue()

    __Thread = None
    __running = False

    __selector_register = None
    __selector_unregister = None

    def start(self, family=AF_UNIX, address='/tmp/relay.sock'):
        # TODO: Already exist exception
        if family == AF_UNIX and exists('/tmp/relay.sock'):
            remove('/tmp/relay.sock')

        super().start(family, address)

    def _setup(self):
        self._socket.bind(self._address)
        self._socket.listen(5)
        return True

    def __accept(self, sock: socket):
        conn, addr = sock.accept()
        print('accepted: {0}, from: {1}'.format(conn, addr))
        conn.setblocking(False)
        self.__selector.register(conn, EVENT_READ)
        self.__connections.append(conn)

    def _selector_handler(self, selector):
        self.__selector = selector
        return self.__accept

    def _recv_handler(self, conn):
        try:
            return conn.recv(4096)
        except OSError:
            self.__close_conn(conn)

    def _error_handler(self, conn):
        self.__close_conn(conn)

    def __close_all_conn(self):
        for conn in self.__connections:
            conn.send('Bye, Bye...'.encode('utf-8'))
            self.__close_conn(conn)

    def __close_conn(self, conn):
        self.__selector.unregister(conn)
        self.__connections.remove(conn)
        conn.close()

    def _teardown(self):
        self.__close_all_conn()
        self.__selector.close()
        self.__running = False
        if self._family == AF_UNIX and exists(self._socket):
            remove(self._socket)

    def update_kW(self, *args, conn=None):
        self.__update(network_api.COM_KILOWATT, args, conn=conn)

    def update_relay(self, *args, conn=None):
        self.__update(network_api.COM_RELAY, args, conn=conn)

    def __update(self, command, data, conn=None):
        self.__create_package(command, network_api.STA_UPDATE, data, conn=conn)

    def __create_package(self, command, status, data, conn=None):
        if conn is None:
            for conn in self.__connections:
                self._send({'COMMAND': command, 'STATUS': status, 'DATA': data}, conn)
        else:
            self._send({'COMMAND': command, 'STATUS': status, 'DATA': data}, conn)

    def _receive(self, package, conn):
        try:
            if isinstance(package, dict):
                if package['COMMAND'] == network_api.COM_KILOWATT:
                    self.__recv_kW(package, conn=conn)
                elif package['COMMAND'] == network_api.COM_RELAY:
                    self.__recv_relay(package, conn=conn)
            else:
                self.__close_conn(conn)
        except (BrokenPipeError, EOFError):
            self.__close_conn(conn)
        except BaseException as e:
            print(e)
            self.__close_conn(conn)

    def __recv_kW(self, package, conn):
        if package['STATUS'] == network_api.STA_UPDATE:
            self.update_kW(watt.get_kW_and_time(), conn=conn)

    def __recv_relay(self, package, conn):
        if package['STATUS'] == network_api.STA_RELOAD:
            self.__create_package(network_api.COM_RELAY,
                               network_api.STA_RELOAD,
                               state_machine.get_relay_full_status(), conn=conn)


server = __ServerAPI()
