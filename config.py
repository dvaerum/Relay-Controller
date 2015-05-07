import configparser
import re
import os.path


class Config:
    class Relay(object):
        __slots__ = ["kilo_watt", "switch_on", "switch_off", "gpio_pin", "relay_number"]

    __file = None
    __config = configparser.ConfigParser()

    __relay = []

    # TODO: Create a config file for this
    __gpio_pins = {"1": 10, "2": 9, "3": 11, "4": 22}

    def __init__(self, filename):
        self.__file = filename

    def load(self):
        # Raise FileNotFoundError if file is missing
        open(self.__file, "r")

        print("Info: Config file loading...")
        self.__config.read(self.__file)



        tmp_relay = []
        for key in self.__config.keys():
            # TODO: Rewrite hardcoding
            match = re.search("Relay[1-4]", key)
            if match:
                tmp_relay.append(self.Relay())
                tmp_relay[-1].kilo_watt = float(self.__config[key]["watt"])
                tmp_relay[-1].switch_on = float(self.__config[key]["koble_ind"])
                tmp_relay[-1].switch_off = float(self.__config[key]["koble_ud"])
                #tmp_relay[-1].gpio_pin = int(self.__config[key]["gpio_pin"])
                tmp_relay[-1].gpio_pin = self.__gpio_pins[match.string[5:]]
                tmp_relay[-1].relay_number = int(match.string[5:])

        if not tmp_relay:
            raise ImportError("There was no relays specified in the config file '{0}'".format(self.__file))

        self.__relay = tmp_relay
        print("Info: Config file Loaded")

    def save(self):
        print("Info: Save config file")

        self.__config["Relay1"] = {}
        self.__config["Relay1"]["watt"] = "10"
        self.__config["Relay1"]["koble_ind"] = "30"
        self.__config["Relay1"]["koble_ud"] = "90"
        self.__config["Relay2"] = {}
        self.__config["Relay2"]["watt"] = "10"
        self.__config["Relay2"]["koble_ind"] = "30"
        self.__config["Relay2"]["koble_ud"] = "90"
        self.__config["Relay3"] = {}
        self.__config["Relay3"]["watt"] = "10"
        self.__config["Relay3"]["koble_ind"] = "30"
        self.__config["Relay3"]["koble_ud"] = "90"
        self.__config["Relay4"] = {}
        self.__config["Relay4"]["watt"] = "10"
        self.__config["Relay4"]["koble_ind"] = "30"
        self.__config["Relay4"]["koble_ud"] = "90"

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