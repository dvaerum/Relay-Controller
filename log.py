from collections import deque
from os import listdir
from os import remove
from queue import Queue
from time import strftime
from threading import Thread
import re


class Log():
    log_queue = Queue()
    path = "etc"
    log_file = None
    thread = None

    def put(self, msg):
        self.log_queue.put(msg)

        if not self.thread or not self.thread.is_alive():
            self.thread = Thread(target=self.__run, name="Thread log.write_log")
            self.thread.start()

    def get_logfile(self):
        files = listdir(self.path)
        log_files = []
        for file in files:
            if re.search(r"Updated [0-2][0-9]\.[0-5][0-9]\.[0-5][0-9] [0-3][0-9]-[0-1][0-9]-[0-9]{4}\.log", file):
                log_files.append(file)

        if len(log_files) == 0:
            self.log_file = None
        elif len(log_files) == 1:
            self.log_file = log_files[0]
        else:
            for file in log_files:
                remove("{0}/{1}".format(self.path, file))
            self.log_file = None

    def __run(self):
        tmp = deque(maxlen=10)
        self.get_logfile()
        if self.log_file:
            with open("{0}/{1}".format(self.path, self.log_file, self.log_file), "r", newline="\r\n") as file:
                for line in reversed(file.read().split("\r\n")):
                    if not line == "None" and not line == "":
                        tmp.appendleft(line)

        while not self.log_queue.empty():
            tmp.appendleft(self.log_queue.get())
            self.log_queue.task_done()

        if self.log_file:
            remove("{0}/{1}".format(self.path, self.log_file))

        tmp2 = ""
        for line in reversed(tmp):
            tmp2 = line + "\r\n" + tmp2

        with open("{0}/Updated {1}.log".format(self.path, strftime("%H.%M.%S %d-%m-%Y")), "w+") as file:
            file.write(tmp2)


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

log_class = Log()


def main():
    log(WARNING, "tester1111")
    log(ERROR, "tester2222")
    log(INFO, "tester3333")
    log(INFO, "tester4444")


if __name__ == '__main__':
    main()