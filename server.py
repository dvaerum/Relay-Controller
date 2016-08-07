#!/usr/bin/env python
import sys
import signal
from os import path

from socket import AF_INET
from tornado.ioloop import IOLoop


from lib.log import logger
from lib.server.server_api import server
from lib.server.web_module import LogSocketHandler, Application

__author__ = 'alt_mulig'


def signal_handler_sigterm(signal = None, frame = None):
    logger.info("Exiting...")

    IOLoop.current().stop()
    server.stop()

    logger.info("Exited")
    sys.exit(0)


def signal_handler_sigkill(signal, frame):
    pass


def main():
    app = Application(path.join(path.dirname(__file__), 'webapps'))
    if len(sys.argv) == 4:
        app.listen(int(sys.argv[3]), address='')
    else:
        app.listen(8002, address='')

    if len(sys.argv) < 3:
        logger.info("")
        signal_handler_sigterm()
    server.start(AF_INET, (sys.argv[1], int(sys.argv[2])))  # TODO: Add exception handling
    server.observe_kW.register(LogSocketHandler)


    signal.signal(signal.SIGTERM, signal_handler_sigterm)
    signal.signal(signal.SIGHUP, signal_handler_sigkill)

    try:
        IOLoop.current().start()
    except KeyboardInterrupt:
        signal_handler_sigterm(None, None)


if __name__ == '__main__':
    main()
