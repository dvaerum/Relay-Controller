from collections import deque
from threading import Thread
from threading import Timer
import time
from state_machine import StateMachine, RelayState
import sys

try:
    import RPIO as GPIO
except SystemError:
    import lib.fakegpio as GPIO


class Watt:
    __pulse = deque([])
    __kW = 0.0

    __event_function = None

    def add_pulse(self, gpio_id, value):
        # TODO: How to handle float overflow (time.perf_counter)
        # TODO: Mads (vismanden) siger at det aldrig sker
        self.__pulse.append(time.perf_counter())

        seconds = self.interval()
        if seconds >= 60:
            self.__kW = (len(self.__pulse) / seconds) / 0.36

            if self.__event_function:
                self.__event_function(self.__kW, seconds)

            while self.interval() >= 60:
                self.__pulse.popleft()
        else:
            print("An Interrupt happened (%.2fs)" % seconds)
            sys.stdout.flush()

    def interval(self):
        return self.__pulse[-1] - self.__pulse[0]

    def set_event_function(self, call_function):
        self.__event_function = call_function


class PI(Thread):
    __watt = Watt()
    __state_machine = StateMachine()

    __relays = []
    __relays_count = 0

    __thread_relay = None
    __thread_fail_safe = None
    __fail_safe_sec = 60.5

    def __init__(self, pin_interrupts):
        Thread.__init__(self)
        self.name = "Thread PI.run"  # Name this thread

        GPIO.add_interrupt_callback(pin_interrupts, self.__watt.add_pulse, edge='rising')
        self.__watt.set_event_function(self.__pass_watt)

    def run(self):
        GPIO.wait_for_interrupts()

    def stop(self):
        GPIO.stop_waiting_for_interrupts()
        GPIO.cleanup()

    def add_relay(self, relay):
        # TODO: event, that shall wait on handle_relay

        for r in relay:
            self.__state_machine.add_relay(
                RelayState(r.kilo_watt,
                           r.switch_on,
                           r.switch_off,
                           r.gpio_pin,
                           r.relay_number))

    def __pass_watt(self, kilo_watt, interval_time):
        # TODO: Make it only print on debug
        print("%.4f kW (%.2fs)" % (kilo_watt, interval_time))
        sys.stdout.flush()

        if not self.__thread_fail_safe or not self.__thread_fail_safe.is_alive():
            if not self.__thread_relay or not self.__thread_relay.is_alive():
                if self.__state_machine.is_started():
                            self.__thread_relay = Thread(target=self.__state_machine.next,
                                                         name="Thread StateMachine.next",
                                                         args=(kilo_watt, interval_time))
                            self.__thread_relay.start()
                else:
                    self.__state_machine.start()

        if self.__thread_fail_safe:
            self.__thread_fail_safe.cancel()
            # TODO: Add time value to the config file
        self.__thread_fail_safe = Timer(self.__fail_safe_sec, self.__fail_safe)

    def __fail_safe(self):
        if not self.__thread_relay or not self.__thread_relay.is_alive():
            # TODO: Make it only print on debug
            print("Runs fail_safe because there hasn't been a pulse in {}s".
                  format(self.__fail_safe_sec))
            sys.stdout.flush()
            self.__state_machine.stop()