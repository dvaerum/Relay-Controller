from configparser import ConfigParser
import re
import os.path
import sys
from lib.observable import Observable
from lib.observer import Observer


class Config(Observer):
    class Relay(object):
        __slots__ = ["kilo_watt", "switch_on", "switch_off", "gpio_pin", "relay_number"]

    observable = Observable()

    __file = None
    __config = ConfigParser()

    __relay = []

    # TODO: Create a config file for this
    __gpio_pins = {"1": 10, "2": 9, "3": 11, "4": 22}

    def __init__(self, filename):
        self.__file = filename

    def update(self, *args, **kwargs):
        self.load()

    def load(self):
        self.__config.clear()

        # Raise FileNotFoundError if file is missing
        open(self.__file, "r")

        print("Info: Config file loading...")
        sys.stdout.flush()
        self.__config.read(self.__file)

        tmp_relay = []
        for section in self.__config.keys():
            # TODO: Rewrite hardcoding
            match = re.search("Relay[1-4]", section)
            if match:
                r = self.__check_relay(section)
                if r:
                    tmp_relay.append(r)

        if not tmp_relay:
            print("Info: There is not defined any relays")
            sys.stdout.flush()
            raise ImportError("There was no relays specified in the config file '{0}'".format(self.__file))

        self.__relay = tmp_relay
        print("Info: Config file Loaded")
        sys.stdout.flush()

        self.observable.update_observers(self.__relay)
        print("Info: Notified observers")
        sys.stdout.flush()

    def __check_relay(self, section):
        tmp = self.Relay()
        try:
            tmp.kilo_watt = self.__to_float(section, "watt")
            tmp.switch_on = self.__to_float(section, "koble_ind")
            tmp.switch_off = self.__to_float(section, "koble_ud")
            tmp.gpio_pin = self.__gpio_pins[section[5:]]
            tmp.relay_number = int(section[5:])
        except ValueError as msg:
            print(msg)
            sys.stdout.flush()
            return None
        return tmp

    def __to_float(self, section, key):
        try:
            value = self.__config[section][key]
        except KeyError:
            raise ValueError("The key '{1}' is missing section '{0}'".format(section, key))

        if not value:
            raise ValueError("The key '{1}', in section '{0}' is undefined".format(section, key))
        return float(value.replace(",", "."))

    def save(self):
        print("Info: Save config file")
        sys.stdout.flush()

        self.__config["Relay1"] = {}
        self.__config["Relay1"]["watt"] = "9.6"
        self.__config["Relay1"]["koble_ind"] = "10"
        self.__config["Relay1"]["koble_ud"] = "90"
        self.__config["Relay2"] = {}
        self.__config["Relay2"]["watt"] = "9.6"
        self.__config["Relay2"]["koble_ind"] = "10"
        self.__config["Relay2"]["koble_ud"] = "60"
        self.__config["Relay3"] = {}
        self.__config["Relay3"]["watt"] = "9.7"
        self.__config["Relay3"]["koble_ind"] = "10"
        self.__config["Relay3"]["koble_ud"] = "60"
        self.__config["Relay4"] = {}
        self.__config["Relay4"]["watt"] = "9.7"
        self.__config["Relay4"]["koble_ind"] = "10"
        self.__config["Relay4"]["koble_ud"] = "60"

        with open(self.__file, "w", newline="\r\n") as configfile:
            self.__config.write(configfile)

    def get_relays(self):
        return self.__relay

def main():
    filename = "etc/test.conf"

    conf = Config(filename)

    if not os.path.isfile(filename):
        conf.save()

    conf.load()
    for r in conf.get_relays():
        print("kW: {0}, switch_on: {1}, switch_off: {2}, gpio_pin: {3}, relay_number: {4}".
              format(r.kilo_watt,
                     r.switch_on,
                     r.switch_off,
                     r.gpio_pin,
                     r.relay_number))


if __name__ == "__main__":
    main()