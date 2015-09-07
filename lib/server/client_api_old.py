from queue import Queue
from socket import gaierror
from time import sleep
from lib import network_api
from lib.observable import Observable

__author__ = 'alt_mulig'


class Client(network_api.NetworkAPI):
    observe_kW = Observable()

    __is_connected = False
    __delay_between_tries = 1.0
    __max_connection_tries = 10

    # TODO: Make this non-hardcoded
    __relays = [False, False, False, False]
    __kilowatt = (0.0, 0.0)

    __update_queue = Queue()
    __running = False
    __Thread = None

    def __init__(self, family, address):
        self.__family = family
        self.__address = address

    def start(self):
        super().start(self.__family, self.__address)

    def _setup(self):
        count = 0
        while not self.__is_connected and count < self.__max_connection_tries:
            try:
                count += 1
                self._socket.connect(self._address)

                self.__is_connected = True
                self.observe_start.register(self.__connected)

                return True
            except (ConnectionRefusedError, FileNotFoundError):
                print("Connecting fail {0} out of {1} tries".format(count, self.__max_connection_tries))
                sleep(self.__delay_between_tries)
            except gaierror as e:
                print("Connecting fail {0} out of {1} tries. It seems that the hostname is wrong".format(count, self.__max_connection_tries))
                sleep(self.__delay_between_tries)

        return False

    def __connected(self):
        self.ask_for_kW_history()
        self.ask_for_relays()

    def __create_package(self, command, status, data):
        self._send({'COMMAND': command, 'STATUS': status, 'DATA': data}, self._socket)

    def ask_for_kW_history(self):
        pass

    def ask_for_relays(self):
        self.__create_package(network_api.COM_RELAY,
                              network_api.STA_RELOAD,
                              None)

    def _receive(self, package, conn):
        if isinstance(package, dict):
            if package['COMMAND'] == network_api.COM_KILOWATT:
                self.__kilowatt = package['DATA']
                self.observe_kW.update_observers(package)
            elif package['COMMAND'] == network_api.COM_RELAY:
                self.__recv_relay(package, conn)

    def __recv_relay(self, package, conn):
        if package['STATUS'] == network_api.STA_UPDATE:
            for relay in self.__relays:
                for package_relay in package['DATA']:
                    if relay[0] == package_relay[0]:
                        relay = package_relay

            self.observe_kW.update_observers(package)
        elif package['STATUS'] == network_api.STA_RELOAD:
            self.__relays = package['DATA']
            self.observe_kW.update_observers(package)

    def is_connected(self):
        return self.__is_connected

    def get_relays(self):
        return self.__relays


def main():
    pass


if __name__ == '__main__':
    main()
