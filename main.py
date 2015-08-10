#!/usr/bin/python

# import sys
# sys.path.append(r'pysrc')
# import pydevd
# pydevd.settrace('Dennis-PC')    # replace IP with address
                                # of Eclipse host machine
import sys
import signal
# TODO: Test if pi_v2 works with main
from pi import PI
from debug import Debug
from config import Config, os
from inotify import Inotify, inotify
from daemon import signal_handler_sigterm, signal_handler_sigkill


def signal_handler(signal, frame):
        print("You pressed Ctrl+C!\nSignal: '{0}'\nFrame: '{1}'".format(signal,frame))
        sys.exit(0)


def main():
    debug = None

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

    signal.signal(signal.SIGTERM, signal_handler_sigterm)
    signal.signal(signal.SIGHUP, signal_handler_sigkill)

    signal.signal(signal.SIGINT, signal_handler)

    str = None
    while not (str == "exit" or str == ""):
        str = input("Write exit to quit.\n")

        print("Debug pulse is set to %s" % str)
        if not debug:
            debug = Debug()

        try:
            debug.set_pulse_timer(float(str))
        except (TypeError, ValueError):
            print("Error happened!!!")

    print("Exiting...")
    debug.stop()
    print("Exited")

if __name__ == "__main__":
    main()

