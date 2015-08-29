from os.path import exists
from os import remove
from queue import Queue, Empty
from selectors import EVENT_READ
from socket import socket
import pickle
from threading import Thread
from time import sleep
from lib import network_api
from lib.observer import Observer

__author__ = 'alt_mulig'


class __ServerAPI(network_api.NetworkAPI, Observer):
    __connections = []
    __update_queue = Queue()

    __Thread = None
    __running = False

    def __init__(self, socket_file):
        # TODO: Already exist exception
        # if exists('/tmp/relay.sock'):
        #     remove('/tmp/relay.sock')

        super().__init__(socket_file=socket_file)

    def update(self, *args, **kwargs):
        self.__update_queue.put(args)

    def __send(self, args):
        if len(args) == 2 and isinstance(args[0], float) and isinstance(args[1], float):
            # TODO: Fix this
            for conn in self.__connections:
                conn.send(pickle.dumps({'COMMAND': network_api.COM_KILOWATT,
                                        'STATUS' : network_api.STA_UPDATE,
                                        'DATA'   : (args[0], args[1])}))

        elif len(args) == 2 and isinstance(args[0], int) and isinstance(args[1], bool):
            # TODO: Fix this
            for conn in self.__connections:
                conn.send(pickle.dumps({'COMMAND': network_api.COM_RELAY,
                                        'STATUS' : network_api.STA_UPDATE,
                                        'DATA'   : (args[0], args[1])}))

        else:
            print("{0} - {1}".format(args[0], args[1]))

        sleep(0.01)

    def __run(self):
        while self.__running:
            try:
                data = self.__update_queue.get(True, 0.1)
                self.__send(data)
            except Empty:
                pass


    def __accept(self, sock: socket):
        conn, addr = sock.accept()
        print('accepted: {0}, from: {1}'.format(conn, addr))
        conn.setblocking(False)
        self._selector.register(conn, EVENT_READ, self.__recv)
        self.__connections.append(conn)

    def __recv(self, conn: socket):
        try:
            data_raw = conn.recv(4096)
            data = pickle.loads(data_raw)
            if isinstance(data, dict):
                if data['COMMAND'] == network_api.COM_KILOWATT:
                    conn.send(pickle.dumps({'COMMAND': network_api.COM_KILOWATT,
                                            'DATA': (9.70, 25.4)}))
            else:
                self.__close_conn(conn)
        except (BrokenPipeError, EOFError):
            self.__close_conn(conn)
        except BaseException as e:
            print(e)
            self.__close_conn(conn)

    def __close_all_conn(self):
        for conn in self.__connections:
            conn.send('Bye, Bye...'.encode('utf-8'))

    def __close_conn(self, conn):
        self._selector.unregister(conn)
        self.__connections.remove(conn)
        conn.close()

    def _setup(self):
        # self._socket.bind(self.socket_file)
        self._socket.bind(('127.0.0.1', self._port))
        self._socket.listen(5)

        if not self.__Thread or not self.__Thread.is_alive():
            self.__running = True
            self.__Thread = Thread(target=self.__run, name='Thread ServerAPI.__run')
            self.__Thread.start()
        return True

    def _teardown(self):
        self.__close_all_conn()
        self.__running = False
        if exists(self.socket_file):
            remove(self.socket_file)

    def _receive(self, sock: socket):
        self.__accept(sock)


server = __ServerAPI('/tmp/relay.sock')


def main():
    server.start()
    input()
    server.stop()


if __name__ == '__main__':
    main()
