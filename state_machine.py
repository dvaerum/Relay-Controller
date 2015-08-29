import time
import sys
from lib.observable import Observable
from lib.observer import Observer

try:
    import RPIO as GPIO
except SystemError:
    import lib.fakegpio as GPIO

from utilities import my_print as print
from utilities import debug_print

debug = False
if len(sys.argv) > 1 and sys.argv[1] == "debug":
    debug = True

# Defines
_OFF = 0
_ON = 1


# class NO:
#     pass
#
#
# class OFF:
#     pass


class RelayState:
    next = None
    prev = None

    __switch_timestamp = 0.0
    __relay_switch_to = None
    __relay_switch_is = _OFF

    def __init__(self, kilo_watt, switch_on, switch_off, gpio_pin, relay_number):

        self.__kilo_watt = kilo_watt
        self.__switch_on = switch_on
        self.__switch_off = switch_off
        self.__gpio_pin = gpio_pin
        self.__relay_number = relay_number

        if self.__relay_number:
            print("Setup Relay {0}".format(self.__relay_number))
            sys.stdout.flush()

    def setup(self):
        # TODO explain why this cannot be inside "__init__"
        GPIO.setup(self.__gpio_pin, GPIO.OUT)
        GPIO.output(self.__gpio_pin, False)

    def get_kilo_watt(self):
        return self.__kilo_watt

    def get_switch_on(self):
        return self.__switch_on

    def get_switch_off(self):
        return self.__switch_off

    def get_gpio_pin(self):
        return self.__gpio_pin

    def get_relay_number(self):
        return self.__relay_number

    def is_relay_on(self):
        if self.__relay_switch_is == _ON:
            return True
        else:
            return False

    def update(self, kilo_watt, switch_on, switch_off):
        self.__kilo_watt = kilo_watt
        self.__switch_on = switch_on
        self.__switch_off = switch_off

    def copy_to(self, instance_to_be_overridden):
        # TODO: raise ValueError if 'gpio_pin' and 'relay_number' is not the same as the one been updated
        instance_to_be_overridden.update(self.__kilo_watt, self.__switch_on, self.__switch_off)

    def __return_state(self, state):
        self.__switch_timestamp = 0.0
        if not state:
            return self
        else:
            return state

    def __next_state(self):
        timestamp = time.perf_counter()
        if not self.__relay_switch_to == _ON or self.__switch_timestamp == 0.0:
            self.__relay_switch_to = _ON
            self.__switch_timestamp = timestamp
        elif timestamp - self.__switch_timestamp > self.__switch_on:
            GPIO.output(self.__gpio_pin, True)
            self.__relay_switch_is = _ON
            return self.__return_state(self.next)

        debug_print("┌───────────────────────────────┐\n│ count = {0:>5.2f}, switch = {1:>5.2f} │".
                    format(timestamp - self.__switch_timestamp, self.__switch_on))
        return self

    def __prev_state(self):
        timestamp = time.perf_counter()
        if not self.__relay_switch_to == _OFF or self.__switch_timestamp == 0.0:
            self.__relay_switch_to = _OFF
            self.__switch_timestamp = timestamp
        elif timestamp - self.__switch_timestamp > self.__switch_off:
            GPIO.output(self.__gpio_pin, False)
            self.__relay_switch_is = _OFF
            return self.__return_state(self.prev)

        debug_print("┌───────────────────────────────┐\n│ count = {0:>5.2f}, switch = {1:>5.2f} │".
                    format(timestamp - self.__switch_timestamp, self.__switch_off))
        return self

    def force_state(self, On_Off):
        if On_Off == _ON:
            GPIO.output(self.__gpio_pin, True)
            return self.__return_state(self.next)
        elif On_Off == _OFF:
            GPIO.output(self.__gpio_pin, False)
            return self.__return_state(self.prev)
        raise ValueError("The input value has to be 'ON' or 'OFF'")

    def run(self, kile_watt):
        if kile_watt > self.__kilo_watt:
            if self.__relay_switch_is == _ON and self.__relay_switch_to == _ON:
                return self.force_state(_ON)
            return self.__next_state()
        elif kile_watt < self.__kilo_watt:
            if self.__relay_switch_is == _OFF and self.__relay_switch_to == _OFF:
                return self.force_state(_OFF)
            return self.__prev_state()
        return self


class StateZero:
    next = None
    prev = None

    def __init__(self):
        self.__relay_number = 0

    def get_relay_number(self):
        return self.__relay_number

    def run(self, kile_watt=None):
        return self.__next_state()

    def __next_state(self):
        return self.__return_state(self.next)

    def __prev_state(self):
        return self.__return_state(self.prev)

    def __return_state(self, state):
        if not state:
            return self
        else:
            return state

    def force_state(self, On_Off):
        if On_Off == _ON:
            return self.__return_state(self.next)
        elif On_Off == _OFF:
            return self.__return_state(self.prev)
        raise ValueError("The input value has to be 'ON' or 'OFF'")


class __StateMachine(Observer):
    __start = None
    __end = None
    __current_state = None

    observe = Observable()

    def __init__(self):
        self.__start = StateZero()
        pass

    def update(self, *args, **kwargs):
        print("{0:.3f} kW ({1:.2f}s)".format(args[0], args[1]))
        sys.stdout.flush()

        if self.is_started():
            self.next(args[0], args[1])
        else:
            # TODO: Find a better solution
            self.start()

    def add_relay(self, new_relay):
        if not self.__start.next:
            new_relay.prev = self.__start
            self.__start.next = new_relay
            self.__end = new_relay
            new_relay.setup()
        else:
            current_state = self.__start.next
            while not new_relay.prev:
                # Updates existing relay
                if current_state and current_state.get_relay_number() == new_relay.get_relay_number():
                    # TODO: fix black python magic. Mads (vismanden)
                    # TODO: siger man kan gøre det med en list istedet for link list.
                    # TODO: og det svære må jeg akende at han har ret
                    new_relay.copy_to(current_state)
                    break
                # Checks that "current_state" is lower then "new_state"
                elif current_state.get_relay_number() < new_relay.get_relay_number():
                    # Checks that "current_state" is the highest number relay that is lower then "new_relay"
                    if current_state.next and (current_state.next.get_relay_number() < new_relay.get_relay_number()
                                               or current_state.next.get_relay_number() == new_relay.get_relay_number()):
                        current_state = current_state.next

                    # Add the new relay
                    else:
                        new_relay.prev = current_state
                        new_relay.next = current_state.next
                        current_state.next = new_relay
                        if not new_relay.next:
                            self.__end = new_relay
                        new_relay.setup()

                # check if "current_state" number is bigger then "new_relay"
                elif current_state.get_relay_number() > new_relay.get_relay_number():
                    # check if this is the last relay and if it is adds the "new_relay" before this one
                    if not current_state.next:
                        tmp = current_state.prev
                        tmp.next = new_relay
                        new_relay.prev = tmp
                        new_relay.next = current_state
                        current_state.prev = new_relay
                        new_relay.setup()
                    else:
                        current_state = current_state.next

    def start(self):
        if not self.is_started():
            if self.__start.next:
                self.__current_state = self.__start.run()

    def next(self, kW, time_interval):
        if self.__current_state:
            temp = self.__current_state
            self.__current_state = self.__current_state.run(kW)
            # if not temp == self.__current_state:
            self.observe.update_observers(self.__current_state.get_relay_number(),
                                              self.__current_state.is_relay_on())

            if debug:
                debug_print_gpio(self)
        else:
            raise IndexError("You have to call start first")

    def stop(self):
        if self.__current_state:
            while not self.__start == self.__current_state:
                self.__current_state = self.__current_state.force_state(_OFF)
            self.__current_state = None

    def is_started(self):
        if self.__current_state:
            return True
        else:
            return False

state_machine = __StateMachine()

def debug_print_gpio(sm):
    current_state = sm._StateMachine__start
    print("├────────┬", end="")
    while True:
        current_state = current_state.next
        if current_state.get_relay_number() == 3:
            print("──────┼", end="")
        elif current_state.get_relay_number() > 3:
            print("──────┐", end="")
        else:
            print("──────┬", end="")
        if not current_state.next:
            break

    current_state = sm._StateMachine__start
    print("\n│ Relay  │", end="")
    while True:
        current_state = current_state.next
        print(" {0:>3}  │".format(current_state.get_relay_number()), end="")
        if not current_state.next:
            break

    current_state = sm._StateMachine__start
    print("\n│ Status │", end="")
    while True:
        current_state = current_state.next
        if current_state._RelayState__relay_switch_is == _ON:
            print(" HIGH │", end="")
        else:
            print(" LOW  │", end="")
        if not current_state.next:
            break

    current_state = sm._StateMachine__start
    print("\n├────────┴", end="")
    while True:
        current_state = current_state.next
        if current_state.get_relay_number() == 3:
            print("──────┼", end="")
        elif current_state.get_relay_number() > 3:
            print("──────┘", end="")
        else:
            print("──────┴", end="")
        if not current_state.next:
            break

    if sm._StateMachine__current_state:
        print("\n│ The current state is: {0:>5} │".format(sm._StateMachine__current_state.get_relay_number()), end="")
        print("\n┴─────────────────────────────┘", end="")

    print("\n", end="")


def main():
    state_machine.add_relay(RelayState(10, 5, 5, 10, 1))
    state_machine.add_relay(RelayState(10, 5, 5, 9, 2))
    state_machine.add_relay(RelayState(10, 5, 5, 11, 3))
    state_machine.add_relay(RelayState(10, 5, 5, 22, 4))
    state_machine.start()

    tmp = None
    while not (tmp == "exit" or tmp == ""):
        tmp = input("kW? ")
        try:
            tmp2 = float(tmp)
            state_machine.next(tmp2, None)
        except (TypeError, ValueError):
            print("Error happened!!!")
        if tmp == "update":
            state_machine.add_relay(RelayState(8, 2, 5, 10, 1))
            state_machine.add_relay(RelayState(8, 2, 5, 9, 2))
            state_machine.add_relay(RelayState(8, 2, 5, 11, 3))
            state_machine.add_relay(RelayState(9, 2, 5, 22, 4))

    state_machine.stop()
    GPIO.cleanup()


if __name__ == "__main__":
    main()