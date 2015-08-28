__author__ = 'Dennis Vestergaard Værum'

from fail_safe import fail_safe
from lib.observer import Observer
from state_machine import StateMachine, RelayState
from watt import watt


class PI(Observer):
    def __init__(self, pin_interrupts):
        self.__pin_interrupts = pin_interrupts
        self.__state_machine = StateMachine()

        fail_safe.set_wait_time(80)
        fail_safe.observe_fail_safe.register(self.__state_machine.stop)

    def start(self):
        self.__state_machine.start()
        watt.observable_kW_update.register(self.__state_machine)
        watt.observable_pulse.register(fail_safe)
        watt.start(self.__pin_interrupts)
        fail_safe.start()

    def stop(self):
        fail_safe.stop()
        watt.stop()
        watt.observable_kW_update.unregister(self.__state_machine)
        watt.observable_pulse.unregister(fail_safe)
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
