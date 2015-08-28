from socket import socket
import pickle
from time import sleep
from lib import network_api
from lib.observable import Observable

__author__ = 'alt_mulig'


class Client(network_api.NetworkAPI):
    __kilowatt = (0.0, 0.0)
    __is_connected = False
    __max_connection_tries = 10
    __delay_between_tries = 1.0

    observe_kW = Observable()

    def _setup(self):
        count = 0
        while not self.__is_connected and count < self.__max_connection_tries:
            try:
                count += 1
                self._socket.connect(self.socket_file)
                self.__is_connected = True
                return True
            except (ConnectionRefusedError, FileNotFoundError):
                print("Connecting fail {0} out of {1} tries".format(count, self.__max_connection_tries))
                sleep(self.__delay_between_tries)

        return False

    def _teardown(self):
        pass

    def _receive(self, conn: socket):
        try:
            data_raw = conn.recv(4096)
            data = pickle.loads(data_raw)
            if isinstance(data, dict):
                if data['COMMAND'] == network_api.COM_KILOWATT:
                    self.__kilowatt = data['DATA']
                    self.observe_kW.update_observers(data['DATA'])
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
