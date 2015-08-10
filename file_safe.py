__author__ = 'alt_mulig'

from lib.observer import Observer
from threading import Thread
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
