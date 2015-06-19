#!/usr/bin/python

# import sys
# sys.path.append(r'pysrc')
# import pydevd
# pydevd.settrace('Dennis-PC')    # replace IP with address
                                # of Eclipse host machine
import sys
import signal
# TODO: Test if pi_v2 works with main
from pi_v2 import PI
from debug import Debug
from config import Config
from inotify import Inotify
from daemon import reload_config_and_apply


def signal_handler(signal, frame):
        print("You pressed Ctrl+C!\nSignal: '{0}'\nFrame: '{1}'".format(signal,frame))
        sys.exit(0)


def main():
    debug = None

    config_file = "etc/config.conf"

    conf = Config(config_file)
    conf.save()
    conf.load()

    gpio = PI(17)
    gpio.add_relay(conf.get_relays())
    gpio.start()

    update_config = Inotify(config_file)
    update_config.set_reload_function(reload_config_and_apply, Config, gpio)
    update_config.start()

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
    gpio.stop()
    update_config.stop()
    print("Exited")

if __name__ == "__main__":
    main()

