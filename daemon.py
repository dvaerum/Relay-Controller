#!/usr/bin/env python

__author__ = 'Dennis Vestergaard Værum'

import sys
import os
import signal
from pi import PI
from config import Config
from inotify import Inotify


pi = None
update_config = None


def reload_config_and_apply(event, *args):
    # @args[0] : Config instance
    # @args[1] : PI instance

    args[0].load()
    args[1].add_relay(args[0].get_relay())


def signal_handler(signal, frame):
    signal_handler_sigterm(signal, frame)


def signal_handler_sigterm(signal, frame):
    print("Exiting...")
    pi.stop()
    update_config.stop()
    print("Exited")
    sys.exit(0)


def signal_handler_sigkill(signal, frame):
    pass


def main():
    global pi
    global update_config

    config_file = "etc/config.conf"
    conf = Config(config_file)

    if not os.path.isfile(config_file):
        conf.save()

    conf.load()

    pi = PI(17)
    pi.add_relay(conf.get_relays())
    pi.start()

    update_config = Inotify(config_file)
    update_config.set_reload_function(reload_config_and_apply, conf, pi)
    update_config.start()

    signal.signal(signal.SIGTERM, signal_handler_sigterm)
    signal.signal(signal.SIGHUP, signal_handler_sigkill)

    while True:
        try:
            signal.pause()
        except KeyboardInterrupt:
            signal_handler_sigterm(None, None)


if __name__ == "__main__":
    main()