from lib.log_v2 import logger
from lib.observable import Observable
from lib.observer import Observer
from threading import Thread
from time import sleep, perf_counter

__author__ = 'alt_mulig'


class __FailSafe(Observer):
    __wait_time = None  # Time to wait before triggering fail safe
    __time_last_updated = None

    __thread = None
    __thread_running = False

    observe_fail_safe = Observable()

    def __init__(self):
        self.__wait_time = 80

    def update(self, *args, **kwargs):
        self.__time_last_updated = perf_counter()

    def start(self):
        self.__thread_running = True
        if not self.__thread or not self.__thread.is_alive():
            self.__thread = Thread(target=self.__run, name="Thread FailSafe.__run")
            self.__thread.start()

    def stop(self):
        self.__thread_running = False

    def __run(self):
        while self.__thread_running:
            if self.__time_last_updated and perf_counter() > self.__time_last_updated + self.__wait_time:
                self.observe_fail_safe.update_observers()
                self.__time_last_updated = None

                # TODO: Make it only print on debug
                logger.info("Runs fail_safe because there hasn't been a pulse in {0}s".format(self.__wait_time))

            sleep(1.0)

    def get_wait_time(self):
        return self.__wait_time

    def set_wait_time(self, wait_time):
        self.__wait_time = wait_time


fail_safe = __FailSafe()
