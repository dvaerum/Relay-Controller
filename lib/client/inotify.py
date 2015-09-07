import pyinotify
from threading import Thread
from lib.observable import Observable
from os.path import exists
from os import remove
from time import sleep
from lib.observer import Observer


class __Inotify():
    __is_run = False
    __thread = None
    __timeout = 1000  # milliseconds

    __files = {}

    def __init__(self):
        pass

    def add_file(self, file):
        if not exists(file):
            raise FileNotFoundError("The file {0} does not exist".format(file))
        elif file not in self.__files:
            self.__files[file] = Observable()
            # self.__add_watch(file) # TODO: Test case for if this code was there
        else:
            raise FileExistsError("The file {0} is already added".format(file))

    def remove_file(self, file):
        if file in self.__files:
            del self.__files[file]
        else:
            raise FileNotFoundError("The file {0} was never added or has already been removed".format(file))

    def register(self, file, observer):
        if file in self.__files:
            self.__files[file].register(observer)
        else:
            raise FileNotFoundError("The file {0} was never added or has been removed".format(file))

    def unregister(self, file, observer):
        if file in self.__files:
            self.__files[file].unregister(observer)
        else:
            raise FileNotFoundError("The file {0} was never added or has been removed".format(file))

    def unregister_all(self, file):
        if file in self.__files:
            self.__files[file].unregister_all()
        else:
            raise FileNotFoundError("The file {0} was never added or has been removed".format(file))

    def start(self):
        if not self.__thread or not self.__thread.is_alive():
            self.__wm = pyinotify.WatchManager()
            self.__notifier = pyinotify.Notifier(self.__wm)
            self.__thread = Thread(target=self.__run, name="Thread Inotify.run")
            self.__thread.start()

    def stop(self):
        self.__is_run = False
        self.__notifier.stop()

    def wait(self):
        self.__thread.join()

    def __run(self):
        self.__is_run = True
        while self.__is_run:
            if self.__notifier.check_events(self.__timeout):
                self.__notifier.read_events()
                self.__notifier.process_events()

            for file in self.__files:
                if not self.__wm.get_wd(file):
                    self.__add_watch(file)

    def __add_watch(self, file):
        if exists(file):
            self.__wm.add_watch(file, pyinotify.IN_MODIFY, proc_fun=self.__files[file].update_observers)


inotify = __Inotify()


class Tester(Observer):
    def update(self, event):
        print(event)

tttt = False
def tester2(file):
    while tttt:
        f = open("etc/{0}".format(file), "w")
        for i in range(0,3):
            f.write("tester\n")
            f.flush()
            sleep(1)
        if exists("etc/{0}".format(file)):
            remove("etc/{0}".format(file))
            sleep(1)

def main():
    global tttt
    # watch_file = Inotify("etc/config.conf")
    # watch_file.set_reload_function(tester1)
    tttt = True
    t = Thread(target=tester2, name="tester2", kwargs={"file": "test.conf"})
    t2 = Thread(target=tester2, name="tester2", kwargs={"file": "herp.conf"})
    t.start()
    t2.start()

    f1 = "etc/test.conf"
    f2 = "etc/test.conf"

    tt = Tester()
    watch_file = inotify

    # TODO: Make test case for this
    watch_file.start()
    sleep(2)
    watch_file.stop()
    sleep(2)
    watch_file.start()

    watch_file.add_file("etc/test.conf")
    # watch_file.add_file("etc/herp.conf")
    watch_file.register("etc/test.conf", tt)
    # watch_file.register("etc/herp.conf", tt)
    input("Press Enter to continue...\n")
    watch_file.stop()
    tttt = False
    print("Exit")
    exit(0)

if __name__ == "__main__":
    main()
