from queue import Queue
from socket import gaierror
from threading import Thread
from time import sleep

from lib import network_api
from lib.log import logger
from lib.client.state_machine import state_machine
from lib.client.watt import watt

__author__ = 'alt_mulig'


class __ClientAPI(network_api.NetworkAPI):
    __is_connected = False
    __delay_between_tries = 1.0
    __max_connection_tries = 10

    __update_queue = Queue()

    __reconnect_thread = None
    __reconnect_running = False

    def _setup(self):
        count = 0
        while not self.__is_connected and count < self.__max_connection_tries:
            try:
                count += 1
                self._socket.connect(self._address)

                self.__is_connected = True
                self.__connected()

                return True
            except (ConnectionRefusedError, FileNotFoundError):
                logger.debug("Connecting fail {0} out of {1} tries".format(count, self.__max_connection_tries))
                sleep(self.__delay_between_tries)
            except gaierror as e:
                logger.debug("Connecting fail {0} out of {1} tries. It seems that the hostname is wrong"
                             .format(count, self.__max_connection_tries))
                sleep(self.__delay_between_tries)

        return False

    def _exception_handler(self, conn, exception):
        if isinstance(exception, EOFError):
            # TODO: Log "Lost connection to server"
            self.stop()
        elif isinstance(exception, BlockingIOError):
            # TODO: Log "Lost connection to server"
            self.stop()
        else:
            raise NotImplementedError('There is not implemented a exception handler for {0}'
                                      .format(exception.__class__.__name__))

    def _teardown(self):
        self.__is_connected = False
        # TODO: Fix this
        if True:
            if not self.__reconnect_thread or not self.__reconnect_thread.is_alive():
                self.__reconnect_thread = Thread(target=self.__reconnect, name="ClientAPI.__run()")
                self.__reconnect_running = True
                self.__reconnect_thread.start()

    def __reconnect(self):
        self.wait()
        while self.__reconnect_running and not self.__is_connected:
            self.start(self._family, self._address)
            if self.__is_connected:
                logger.info("Connected to Server")
                self.__reconnect_running = False
            else:
                logger.info("Tries the connect again")
                sleep(1)

    def __connected(self):
        with open('user.txt') as u:
            with open('pass.txt') as p:
                self.__create_package(network_api.COM_LOGIN,
                                      network_api.STA_USER,
                                      (u.read(), p.read()))

    def stop(self):
        if self.__reconnect_thread:
            self.__reconnect_running = False
            self.__reconnect_thread.join()
        super().stop()

    def _receive(self, package, conn):
        def __recv_kW(package):
            if package['STATUS'] == network_api.STA_UPDATE:
                self.update_kW(watt.get_kW_and_time())

        def __recv_relay(package):
            if package['STATUS'] == network_api.STA_RELOAD:
                self.__create_package(network_api.COM_RELAY,
                                      network_api.STA_RELOAD,
                                      state_machine.get_relay_full_status())

        try:
            if isinstance(package, dict):
                if package['COMMAND'] == network_api.COM_KILOWATT:
                    __recv_kW(package)
                elif package['COMMAND'] == network_api.COM_RELAY:
                    __recv_relay(package)
        except None:
            pass

    def __create_package(self, command, status, data):
        self._send({'COMMAND': command, 'STATUS': status, 'DATA': data}, self._socket)

    def update_kW(self, *args):
        if self.__is_connected:
            self.__update(network_api.COM_KILOWATT, args)

    def update_relay(self, *args):
        self.__update(network_api.COM_RELAY, args)

    def __update(self, command, data):
        self.__create_package(command, network_api.STA_UPDATE, data)


client = __ClientAPI()


def main():
    pass


if __name__ == '__main__':
    main()
