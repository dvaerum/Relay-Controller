import time
from collections import deque

from lib.log import logger
from lib.observable import Observable

__author__ = 'alt_mulig'

try:
    import RPIO as GPIO
except SystemError:
    import lib.client.fakegpio as GPIO


class __Watt:
    observable_pulse = Observable()
    observable_kW_update = Observable()

    __pulse = deque([])

    __kW = 0.0
    __seconds = 0

    __max_time = 60
    __max_pulses = 5
    # TODO: create a variable to hold the value for "debounce_timeout_ms"

    __pin_interrupts = None

    def start(self, pin_interrupts):
        if self.__pin_interrupts:
            GPIO.del_interrupt_callback(self.__pin_interrupts)
        self.__pin_interrupts = pin_interrupts

        GPIO.add_interrupt_callback(self.__pin_interrupts, self.__add_pulse, edge='rising', debounce_timeout_ms=100)
        GPIO.wait_for_interrupts(threaded=True)

    def stop(self):
        GPIO.stop_waiting_for_interrupts()

    def wait(self):
        # TODO: Make A join
        time.sleep(1.0)

    def __add_pulse(self, gpio_id, value):
        # TODO: How to handle float overflow (time.perf_counter)
        # TODO: Mads (vismanden) siger at det aldrig vil ske
        self.__pulse.append(time.perf_counter())

        self.observable_pulse.update_observers()

        seconds = self.__interval()
        if len(self.__pulse) >= self.__max_pulses:
            self.__calc_kW(seconds)

            while len(self.__pulse) >= self.__max_pulses:
                self.__pulse.popleft()
        elif seconds >= self.__max_time:
            self.__calc_kW(seconds)

            while self.__interval() >= self.__max_time:
                self.__pulse.popleft()
        else:
            logger.debug("An Interrupt happened ({0:.2f}s)".format(seconds))

    def __interval(self):
        return self.__pulse[-1] - self.__pulse[0]

    def __calc_kW(self, seconds):
        self.__kW = ((len(self.__pulse)) / seconds) / 0.036
        self.__seconds = 0
        self.observable_kW_update.update_observers(self.__kW, seconds)

    def get_kW_and_time(self):
        return self.__kW, self.__seconds


watt = __Watt()
