from collections import deque
from os import listdir
from os import remove
from queue import Queue
from time import strftime
from threading import Thread
import re


class Log():
    __log_queue = Queue()
    __log_file = None
    __thread = None

    def __init__(self, path):
        self.__path = path

    def get(self):
        return self.__path

    def put(self, msg):
        self.__log_queue.put(msg)
        if not self.__thread or not self.__thread.is_alive():
            self.__thread = Thread(target=self.run, name="Thread log.write_log")
            self.__thread.start()

    def get_logfile(self):
        files = listdir(self.__path)
        log_files = []
        for file in files:
            if re.search(r"Updated [0-2][0-9]\.[0-5][0-9]\.[0-5][0-9] [0-3][0-9]-[0-1][0-9]-[0-9]{4}\.log", file):
                log_files.append(file)

        if len(log_files) == 0:
            self.__log_file = None
        elif len(log_files) == 1:
            self.__log_file = log_files[0]
        else:
            for file in log_files:
                remove("{0}/{1}".format(self.__path, file))
            self.__log_file = None

    # TODO: Give this method a real name
    def herp(self):
        tmp = deque(maxlen=10)
        self.get_logfile()
        if self.__log_file:
            with open("{0}/{1}".format(self.__path, self.__log_file, self.__log_file), "r", newline="\r\n") as file:
                for line in reversed(file.read().split("\r\n")):
                    if not line == "None" and not line == "":
                        tmp.appendleft(line)

        while not self.__log_queue.empty():
            tmp.appendleft(self.__log_queue.get())
            self.__log_queue.task_done()

        if self.__log_file:
            remove("{0}/{1}".format(self.__path, self.__log_file))

        tmp2 = ""
        for line in reversed(tmp):
            tmp2 = line + "\r\n" + tmp2

        return tmp2

    def run(self):
        with open("{0}/Updated {1}.log".format(self.__path, strftime("%H.%M.%S %d-%m-%Y")), "w+") as file:
            file.write(self.herp())


def log(status, msg):
    time = strftime("%H:%M:%S %d/%m-%Y")
    if status is WARNING:
        msg = "[{0}][{1}] {2}".format(time, WARNING, msg)
    elif status is INFO:
        msg = "[{0}][{1}] {2}".format(time, INFO, msg)
    elif status is ERROR:
        msg = "[{0}][{1}] {2}".format(time, ERROR, msg)

    log_class.put(msg)


WARNING = "WARNING"
INFO = "INFO"
ERROR = "ERROR"

log_class = Log("etc")


def main():
    log(WARNING, "tester1111")
    log(ERROR, "tester2222")
    log(INFO, "tester3333")
    log(INFO, "tester4444")


if __name__ == '__main__':
    main()