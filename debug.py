from time import sleep
from threading import Thread
try:
    import RPIO as GPIO
except SystemError:
    import lib.fakegpio as GPIO


class Debug:
    __time_between_pulse = None
    __thread_wait = None
    __thread_pulse = None
    __running_wait = None

    __gpio_pin = 7

    def __init__(self):
        GPIO.setup(self.__gpio_pin, GPIO.OUT)
        GPIO.output(self.__gpio_pin, False)

    def set_pulse_timer(self, time):
        self.__time_between_pulse = time
        if not self.__thread_wait or not self.__thread_wait.isAlive():
            self.__running_wait = True
            self.__thread_wait = Thread(target=self.__wait, name="Thread Debug.__wait")
            self.__thread_wait.start()

    def stop(self):
            self.__running_wait = False

    def __wait(self):
        while (self.__running_wait):
            if not self.__thread_pulse or not self.__thread_pulse.isAlive():
                self.__thread_pulse = Thread(target=self.__pulse, name="Thread Debug.__pulse")
                self.__thread_pulse.start()

            sleep(self.__time_between_pulse)

    def __pulse(self):
        GPIO.output(self.__gpio_pin, True)
        sleep(1.0/1000.0*50.0)
        GPIO.output(self.__gpio_pin, False)