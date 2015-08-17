import unittest
import threading
from inotify import inotify
from os import remove
from os.path import exists
from time import sleep
from lib.observer import Observer


__author__ = 'Dennis Værum'


class TestInotify(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.filename = "etc/test.conf"
        cls.file = open(cls.filename, "w")
        cls.notify = Notify()

        inotify.start()
        inotify.add_file(cls.filename)
        inotify.register(cls.filename, cls.notify)

    def tearDown(self):
        self.notify.reset()

    @classmethod
    def tearDownClass(cls):
        inotify.stop()
        if exists(cls.filename):
            remove(cls.filename)

    def test_file_not_existing(self):
        with self.assertRaises(FileNotFoundError):
            inotify.add_file("herp.derp")
        with self.assertRaises(FileNotFoundError):
            inotify.register("herp.derp", self.notify)
        with self.assertRaises(FileNotFoundError):
            inotify.unregister("herp.derp", self.notify)
        with self.assertRaises(FileNotFoundError):
            inotify.unregister_all("herp.derp")

    def test_file_exists(self):
        with self.assertRaises(FileExistsError):
            inotify.add_file(self.filename)

    def test_file_change(self):
        self.assertFalse(self.notify.get())
        self.file.write("In the name of Søren Jensen\nherp derp, that shit!\n")
        self.file.flush()
        sleep(1)
        self.assertTrue(self.notify.get())

    def test_remove_and_add_file(self):
        inotify.remove_file(self.filename)
        inotify.add_file(self.filename)

    def test_unregister_and_register(self):
        inotify.unregister(self.filename, self.notify)
        inotify.register(self.filename, self.notify)

    def test_unregister_all(self):
        inotify.unregister_all(self.filename)
        inotify.register(self.filename, self.notify)

    def test_stop_and_start(self):
        if self.__too_many_threads(1):
            self.fail('There are too many Threads with the name "Thread Inotify.run"')
        inotify.stop()
        sleep(2)
        if self.__too_many_threads(0):
            self.fail('There is more then one Threads with the name "Thread Inotify.run"')
        inotify.start()
        sleep(1)
        if self.__too_many_threads(1):
            self.fail('There are too many Threads with the name "Thread Inotify.run"')

    def __too_many_threads(self, number):
        count = 0
        for thread in threading.enumerate():
            if thread._name == 'Thread Inotify.run':
                count += 1
        if count > number:
            return True
        return False

    def test_delete_and_create_file(self):
        pass
        # I don't know how to test this


class Notify(Observer):
    __notified = False

    def update(self, *args, **kwargs):
        self.__notified = True

    def reset(self):
        self.__notified = False

    def get(self):
        return self.__notified


if __name__ == '__main__':
    unittest.main()
