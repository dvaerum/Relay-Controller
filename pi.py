__author__ = 'Dennis Vestergaard Værum'

from threading import Thread
from lib.observer import Observer
from state_machine import StateMachine, RelayState
from watt import watt
import time
import sys

class FailSafe(Observer):
    __wait_time = None  # Time to wait before triggering fail safe
    __time_last_updated = None

    __thread = None
    __thread_running = False
    __fail_safe_function = None

    def __init__(self, wait_time, fail_safe_function):
        self.__wait_time = wait_time
        self.__fail_safe_function = fail_safe_function

    def update(self, *args, **kwargs):
        self.__time_last_updated = time.perf_counter()

    def start(self):
        self.__thread_running = True
        if not self.__thread or not self.__thread.is_alive():
            self.__thread = Thread(target=self.__run,
                                   name="Thread FailSafe.__run")
            self.__thread.start()

    def stop(self):
        self.__thread_running = False

    def __run(self):
        while self.__thread_running:
            if self.__time_last_updated and \
                    time.perf_counter() > self.__time_last_updated + self.__wait_time:

                # TODO: Make it only print on debug
                print("Runs fail_safe because there hasn't been a pulse in {0}s".
                      format(self.__wait_time))
                sys.stdout.flush()
                self.__fail_safe_function()

            time.sleep(1.0)


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
