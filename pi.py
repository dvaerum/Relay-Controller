__author__ = 'Dennis Vestergaard Værum'

from file_safe import FailSafe
from lib.observer import Observer
from state_machine import StateMachine, RelayState
from watt import watt


class PI(Observer):
    __state_machine = StateMachine()
    __fail_safe = FailSafe(80, __state_machine.stop)

    def __init__(self, pin_interrupts):
        self.__pin_interrupts = pin_interrupts

    def start(self):
        self.__state_machine.start()
        watt.observable_kW_update.register(self.__state_machine)
        watt.observable_pulse.register(self.__fail_safe)
        watt.start(self.__pin_interrupts)
        self.__fail_safe.start()

    def stop(self):
        self.__fail_safe.stop()
        watt.stop()
        watt.observable_kW_update.unregister(self.__state_machine)
        watt.observable_pulse.unregister(self.__fail_safe)
        self.__state_machine.stop()

    def update(self, relay):
        self.add_relay(relay)

    def add_relay(self, relay):
        # TODO: event, that shall wait on handle_relay

        for r in relay:
            self.__state_machine.add_relay(
                RelayState(r.kilo_watt,
                           r.switch_on,
                           r.switch_off,
                           r.gpio_pin,
                           r.relay_number))
