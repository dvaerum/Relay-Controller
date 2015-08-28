from time import sleep
from fail_safe import fail_safe
from lib.observer import Observer
import unittest

__author__ = 'alt_mulig'


class MyTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.notify = Notify()
        fail_safe.set_wait_time(3)
        fail_safe.observe_fail_safe.register(cls.notify.update)
        fail_safe.start()

    @classmethod
    def tearDownClass(cls):
        fail_safe.stop()

    def test_something(self):
        self.notify.reset()
        fail_safe.update()
        sleep(2)
        self.assertFalse(self.notify.get())

        fail_safe.update()
        sleep(2)
        self.assertFalse(self.notify.get())

        sleep(2)
        self.assertTrue(self.notify.get())


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
