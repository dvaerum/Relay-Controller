from threading import Thread
from time import sleep
from lib.log_v2 import logger

logger.info("Loading library: {0}".format(__name__))


pins = {"1": 10, "2": 9, "3": 11, "4": 22}
OUT = 1
IN = 2


interrupt = None

def setup(gpio_pin, in_out):
    pass


def output(gpio_pin, high_low):
    for v in pins:
        if pins[v] == gpio_pin:
            logger.debug("Relay[{0}] is {1}".format(v, "HIGH" if high_low else "LOW"))


def main():
    output(11, True)
    output(9, False)


def add_interrupt_callback(gpio_pin, func, **kwargs):
    global interrupt
    if not interrupt:
        interrupt = FakeGPIO(gpio_pin, func)


def wait_for_interrupts(threaded=True):
    global interrupt
    interrupt.set_pulse_timer(3.05)


def stop_waiting_for_interrupts():
    global interrupt
    interrupt.stop()


def cleanup():
    global interrupt
    interrupt.stop()


class FakeGPIO:
    __time_between_pulse = None
    __thread_wait = None
    __thread_pulse = None
    __running_wait = None

    __gpio_pin = None
    __func = None

    def __init__(self, gpio_pin, func):
        self.__gpio_pin = gpio_pin
        self.__func = func

    def set_pulse_timer(self, time):
        self.__time_between_pulse = time
        if not self.__thread_wait or not self.__thread_wait.isAlive():
            self.__running_wait = True
            self.__thread_wait = Thread(target=self.__wait, name="Thread FakeGPIO.__wait")
            self.__thread_wait.start()

    def stop(self):
            self.__running_wait = False

    def __wait(self):
        while (self.__running_wait):
            if not self.__thread_pulse or not self.__thread_pulse.isAlive():
                self.__thread_pulse = Thread(target=self.__pulse, name="Thread FakeGPIO.__pulse")
                self.__thread_pulse.start()

            sleep(self.__time_between_pulse)

    def __pulse(self):
        self.__func(self.__gpio_pin, True)

if __name__ == "__main__":
    main()