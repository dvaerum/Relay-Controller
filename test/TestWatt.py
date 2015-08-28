from collections import deque
from time import sleep
from lib.observer import Observer
import unittest
from watt import watt

__author__ = 'alt_mulig'


class MyTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.n_pulse = Notify()
        cls.n_kW = Notify()
        watt.observable_pulse.register(cls.n_pulse)
        watt.observable_kW_update.register(cls.n_kW)

    def setUp(self):
        watt._Watt__pulse = deque([])
        self.n_kW.reset()
        self.n_pulse.reset()

    @classmethod
    def tearDownClass(cls):
        pass

    def test___add_pulse_normal(self):
        watt.start(17)

        count = 0
        while not self.n_kW.get():
            if self.n_pulse.get():
                count += 1
                self.n_pulse.reset()

            sleep(0.05)

        self.assertLess(count, 5)
        watt.stop()

    def test___add_pulse_manuel(self):
        watt._Watt__add_pulse(17, None)
        self.assertTrue(self.n_pulse.get())
        self.assertFalse(self.n_kW.get())
        watt._Watt__add_pulse(17, None)
        self.assertTrue(self.n_pulse.get())
        self.assertFalse(self.n_kW.get())
        watt._Watt__add_pulse(17, None)
        self.assertTrue(self.n_pulse.get())
        self.assertFalse(self.n_kW.get())
        watt._Watt__add_pulse(17, None)
        self.assertTrue(self.n_pulse.get())
        self.assertFalse(self.n_kW.get())
        watt._Watt__add_pulse(17, None)
        self.assertTrue(self.n_pulse.get())
        self.assertTrue(self.n_kW.get())
        watt._Watt__add_pulse(17, None)
        self.assertTrue(self.n_pulse.get())
        self.assertTrue(self.n_kW.get())

    def test___add_pulse_longer_then_one_minute(self):
        watt._Watt__add_pulse(17, None)
        self.assertTrue(self.n_pulse.get())
        self.assertFalse(self.n_kW.get())
        watt._Watt__add_pulse(17, None)
        self.assertTrue(self.n_pulse.get())
        self.assertFalse(self.n_kW.get())

        print("waited {0}s out if 60s".format(0))
        for i in range(5, 61, 5):
            sleep(5)
            print("waited {0}s out if 60s".format(i))

        watt._Watt__add_pulse(17, None)
        self.assertTrue(self.n_pulse.get())
        self.assertTrue(self.n_kW.get())
        watt._Watt__add_pulse(17, None)
        self.assertTrue(self.n_pulse.get())
        self.assertTrue(self.n_kW.get())


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