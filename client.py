#!/usr/bin/env python
import sys
import os
import signal
from socket import AF_INET, AF_UNIX

from lib.log import logger
from lib.client.pi import PI
from lib.client.config import Config
from lib.client.inotify import inotify
from lib.client.client_api import client
from lib.client.state_machine import state_machine
from lib.client.watt import watt

__author__ = 'Dennis Vestergaard Værum'

pi = None

def signal_handler(signal, frame):
    signal_handler_sigterm(signal, frame)


def signal_handler_sigterm(signal, frame):
    logger.info("Exiting...")
    inotify.stop()
    pi.stop()
    client.stop()

    inotify.wait()
    pi.wait()

    logger.info("Exited")
    sys.exit(0)


def signal_handler_sigkill(signal, frame):
    pass


def main():
    global pi

    config_file = "etc/config.conf"
    conf = Config(config_file)

    if not os.path.isfile(config_file):
        conf.save()

    pi = PI(17)
    conf.observable.register(pi)

    conf.load()

    pi.start()

    inotify.add_file(config_file)
    inotify.register(config_file, conf)
    inotify.start()

    if len(sys.argv) == 3:
        client.start(family=AF_INET, address=(sys.argv[1], int(sys.argv[2])))
    else:
        client.start(family=AF_UNIX, address='/tmp/relay.sock')

    watt.observable_kW_update.register(client.update_kW)
    state_machine.observe_change.register(client.update_relay)

    signal.signal(signal.SIGTERM, signal_handler_sigterm)
    signal.signal(signal.SIGHUP, signal_handler_sigkill)

    while True:
        try:
            signal.pause()
        except KeyboardInterrupt:
            signal_handler_sigterm(None, None)


if __name__ == "__main__":
    main()
