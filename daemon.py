#!/usr/bin/env python
from socket import AF_INET, AF_UNIX
import sys
import os
import signal
from pi import PI
from config import Config
from inotify import inotify
from server_api import server
from state_machine import state_machine
from watt import watt

__author__ = 'Dennis Vestergaard Værum'

pi = None


def signal_handler(signal, frame):
    signal_handler_sigterm(signal, frame)


def signal_handler_sigterm(signal, frame):
    print("Exiting...")
    inotify.stop()
    pi.stop()
    server.stop()
    print("Exited")
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

    # pi.add_relay(conf.get_relays())
    pi.start()

    inotify.add_file(config_file)
    inotify.register(config_file, conf)
    inotify.start()

    if len(sys.argv) == 3:
        server.start(family=AF_INET, address=(sys.argv[1], int(sys.argv[2])))
    else:
        server.start(family=AF_UNIX, address='/tmp/relay.sock')

    watt.observable_kW_update.register(server)
    state_machine.observe.register(server)

    signal.signal(signal.SIGTERM, signal_handler_sigterm)
    signal.signal(signal.SIGHUP, signal_handler_sigkill)

    while True:
        try:
            signal.pause()
        except KeyboardInterrupt:
            signal_handler_sigterm(None, None)


if __name__ == "__main__":
    main()
