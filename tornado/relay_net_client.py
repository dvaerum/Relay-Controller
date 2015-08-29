from queue import Queue, Empty
from socket import socket
import pickle
from threading import Thread
from time import sleep
from lib import network_api
from lib.observable import Observable

__author__ = 'alt_mulig'


class Client(network_api.NetworkAPI):
    __is_connected = False
    __max_connection_tries = 10
    __delay_between_tries = 1.0

    __kilowatt = (0.0, 0.0)
    # TODO: Make this non-hardcoded
    __relay = [False, False, False, False]

    observe_kW = Observable()

    __update_queue = Queue()
    __Thread = None
    __running = False

    def _setup(self):
        count = 0
        while not self.__is_connected and count < self.__max_connection_tries:
            try:
                count += 1
                # self._socket.connect(self.socket_file)
                self._socket.connect(('127.0.0.1', self._port))
                self.__is_connected = True

                if not self.__Thread or not self.__Thread.is_alive():
                    self.__running = True
                    self.__Thread = Thread(target=self.__run, name='Thread ServerAPI.__run')
                    self.__Thread.start()

                return True
            except (ConnectionRefusedError, FileNotFoundError):
                print("Connecting fail {0} out of {1} tries".format(count, self.__max_connection_tries))
                sleep(self.__delay_between_tries)

        return False

    def __run(self):
        while self.__running:
            try:
                data = self.__update_queue.get(True, 0.5)
                if data['COMMAND'] == network_api.COM_KILOWATT:
                    self.__kilowatt = data['DATA']
                    self.observe_kW.update_observers(data)
                elif data['COMMAND'] == network_api.COM_RELAY:
                    if data['DATA'][0] > 1:
                        self.__relay[data['DATA'][0] - 2] = True

                    self.__relay[data['DATA'][0] - 1] = data['DATA'][1]

                    if data['DATA'][0] < 4:
                        self.__relay[data['DATA'][0] - 0] = False

                    data["DATA"] = self.__relay
                    self.observe_kW.update_observers(data)
            except Empty:
                pass

    def _teardown(self):
        self.__running = False

    def _receive(self, conn: socket):
        try:
            data_raw = conn.recv(4096)
            data = pickle.loads(data_raw)
            if isinstance(data, dict):
                self.__update_queue.put(data)
        except (EOFError, BlockingIOError):
            # TODO: Log "Lost connection to server"
            self.__is_connected = False
            self.stop()
        # except BaseException as e:
        #     print(e)
        #     self.__is_connected = False
        #     self.stop()

    def is_connected(self):
        return self.__is_connected

    def get_kilowatt(self):
        return self.__kilowatt


def main():
    pass


if __name__ == '__main__':
    main()
