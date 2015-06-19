__author__ = 'Dennis Vestergaard Værum'

from collections import deque
from threading import Thread
import time
from lib.observable import Observable
from lib.observer import Observer
from state_machine import StateMachine, RelayState
import sys

try:
    import RPIO as GPIO
except SystemError:
    import lib.fakegpio as GPIO


class Watt:
    observable_pulse = Observable()
    observable_kW_update = Observable()

    __pulse = deque([])
    __kW = 0.0

    __pin_interrupts = None

    # TODO: Make it sow the start cannot be called if it is already running
    def start(self, pin_interrupts):
        if self.__pin_interrupts:
            GPIO.del_interrupt_callback(self.__pin_interrupts)
        self.__pin_interrupts = pin_interrupts

        GPIO.add_interrupt_callback(self.__pin_interrupts, self.__add_pulse, edge='rising')
        GPIO.wait_for_interrupts(threaded=True)

    def stop(self):
        GPIO.stop_waiting_for_interrupts()

    def __add_pulse(self, gpio_id, value):
        # TODO: How to handle float overflow (time.perf_counter)
        # TODO: Mads (vismanden) siger at det aldrig sker
        self.__pulse.append(time.perf_counter())

        self.observable_pulse.update_observers()

        seconds = self.__interval()
        if seconds >= 60:
            self.__kW = (len(self.__pulse) / seconds) / 0.036

            self.observable_kW_update.update_observers(self.__kW, seconds)

            while self.__interval() >= 60:
                self.__pulse.popleft()
        else:
            print("An Interrupt happened (%.2fs)" % seconds)
            sys.stdout.flush()

    def __interval(self):
        return self.__pulse[-1] - self.__pulse[0]


watt = Watt()


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


class PI:
    __state_machine = StateMachine()
    __fail_safe = FailSafe(80, __state_machine.stop)

    def __init__(self, pin_interrupts):
        self.__pin_interrupts = pin_interrupts

    def start(self):
        self.__state_machine.start()
        watt.observable_kW_update.register(self.__state_machine)
        watt.observable_pulse.register(self.__fail_safe)
        watt.start(self.__pin_interrupts)

    def stop(self):
        watt.stop()
        watt.observable_kW_update.unregister(self.__state_machine)
        watt.observable_pulse.unregister(self.__fail_safe)
        self.__state_machine.stop()

    def add_relay(self, relay):
        # TODO: event, that shall wait on handle_relay

        for r in relay:
            self.__state_machine.add_relay(
                RelayState(r.kilo_watt,
                           r.switch_on,
                           r.switch_off,
                           r.gpio_pin,
                           r.relay_number))
