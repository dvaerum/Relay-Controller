import pyinotify
from threading import Thread


class Inotify(Thread):
    __reload_function = None
    __reload_function_args = None
    __run = None
    __timeout = 1000  # milliseconds

    def __init__(self, config_file):
        Thread.__init__(self)
        self.name="Thread Inotify.run"
        
        self.__config_file = config_file

        self.wm = pyinotify.WatchManager()
        self.notifier = pyinotify.Notifier(self.wm)
        self.__add_watch()

    def run(self):
        self.__run = True
        while self.__run:
            if self.notifier.check_events(self.__timeout):
                self.notifier.read_events()
                self.notifier.process_events()

                if not self.wm.get_wd(self.__config_file):
                    self.__add_watch()

    def __add_watch(self):
        self.wm.add_watch(self.__config_file, pyinotify.IN_MODIFY, proc_fun=self.__reload)

    def stop(self):
        self.__run = False
        self.notifier.stop()

    def __reload(self, event):
        if self.__reload_function:
            self.__reload_function(event, *self.__reload_function_args)

    def set_reload_function(self, reload_function, *args):
        self.__reload_function = reload_function
        self.__reload_function_args = args
        

def tester(event):
    print(event)


def main():
    watch_file = Inotify("config.conf")
    watch_file.set_reload_function(tester)
    watch_file.start()
    input("Press Enter to continue...\n")
    watch_file.stop()
    print("Exit")

if __name__ == "__main__":
    main()