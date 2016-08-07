from os.path import exists
from os import remove
from queue import Queue
from selectors import EVENT_READ
from socket import socket, AF_UNIX
import time
from lib import network_api
from lib.log import logger
from lib.observable import Observable

__author__ = 'alt_mulig'


class __ServerAPI(network_api.NetworkAPI):
    class Connection:
        logged_in = None
        connection_time = None

        def __init__(self, connection_time):
            self.connection_time = connection_time

    observe_kW = Observable()

    # TODO: Make this non-hardcoded
    __relays = [(1, False), (2, False), (3, False), (4, False)]
    __kilowatt = (0.0, 0.0)

    __connections = {}
    __update_queue = Queue()

    __selector = None

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
        logger.debug('accepted: {0}, from: {1}'.format(conn, addr))
        conn.setblocking(False)
        self.__selector.register(conn, EVENT_READ)
        self.__connections[conn] = self.Connection(time.time())
        self.__connected(conn)

    def _selector_handler(self, selector):
        self.__selector = selector
        return self.__accept

    def _exception_handler(self, conn, exception):
        if isinstance(exception, EOFError):
            # TODO: Log "Lost connection to server"
            self.__close_conn(conn)
        elif isinstance(exception, BlockingIOError):
            # TODO: Log "Lost connection to server"
            self.__close_conn(conn)
        elif isinstance(exception, OSError):
            # TODO: Log "Lost connection to server"
            self.__close_conn(conn)
        else:
            raise NotImplementedError('There is not implemented a exception handler for {0}'
                                      .format(exception.__class__.__name__))

    def __close_all_conn(self):
        for conn in self.__connections:
            conn.send('Bye, Bye...'.encode('utf-8'))
            self.__close_conn(conn)

    def __close_conn(self, conn):
        self.__selector.unregister(conn)
        del self.__connections[conn]
        conn.close()

    def _teardown(self):
        self.__close_all_conn()
        self.__running = False
        if self._family == AF_UNIX and exists(self._address):
            remove(self._address)

    def get_relays(self):
        return self.__relays

    def __create_package(self, command, status, data, conn=None):
        if conn:
            self._send({'COMMAND': command, 'STATUS': status, 'DATA': data}, conn)
        else:
            for conn in self.__connections:
                self._send({'COMMAND': command, 'STATUS': status, 'DATA': data}, conn)

    def __connected(self, conn):
        def ask_for_kW_history(conn):
            pass

        def ask_for_relays(conn):
            self.__create_package(network_api.COM_RELAY,
                                  network_api.STA_RELOAD,
                                  None, conn)

        ask_for_kW_history(conn)
        ask_for_relays(conn)

    def _receive(self, package, conn):
        def __recv_relay(package, conn):
            if package['STATUS'] == network_api.STA_UPDATE:
                for relay in self.__relays:
                    for package_relay in package['DATA']:
                        if relay[0] == package_relay[0]:
                            relay = package_relay

                package['DATA'] = self.__relays  # Sends all the states of all the relays
                self.observe_kW.update_observers(package)
            elif package['STATUS'] == network_api.STA_RELOAD:
                self.__relays = package['DATA']
                self.observe_kW.update_observers(package)

        if isinstance(package, dict):
            if self.__connections[conn].logged_in:
                if package['COMMAND'] == network_api.COM_KILOWATT:
                    self.__kilowatt = package['DATA']
                    self.observe_kW.update_observers(package)
                elif package['COMMAND'] == network_api.COM_RELAY:
                    __recv_relay(package, conn)
            else:
                if package['COMMAND'] == network_api.COM_LOGIN:
                    # TODO: Add support for cookies
                    if package['STATUS'] == network_api.STA_USER:
                        # TODO: Fix Hardcoding
                        with open('user.txt') as u:
                            with open('pass.txt') as p:
                                if package['DATA'][0] == u.read() and package['DATA'][1] == p.read():
                                    self.__connections[conn].logged_in = 1337
                                    self.__connected(conn)
                else:
                    if self.__connections[conn].connection_time > time.time() + 60:
                        logger.debug('Closed connection to {0}, because the client had not logged in within a 60s'
                                     .format(conn.family))
                        self.__close_conn(conn)
        else:
            logger.debug('Closed connection to {0}'.format(conn.family))
            self.__close_conn(conn)


server = __ServerAPI()
