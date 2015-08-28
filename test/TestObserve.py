__author__ = 'chad.lung'
__doc__ = 'http://www.giantflyingsaucer.com/blog/?p=5117'

import unittest

from lib.observable import Observable
from lib.observer import Observer


def an_function(*args, **kwargs):
    return


class AnClass:
    update = 3


class AnObserver(Observer):
    def __init__(self):
        self.args = []
        self.kwargs = {}

    def update(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        return


class TestObserve(unittest.TestCase):

    def setUp(self):
        self.observable = Observable()

        self.observer1 = AnObserver()
        self.observer2 = AnObserver()
        self.observer3 = AnObserver()

    def test_remove_all(self):
        self.observable.register(self.observer1)
        self.observable.register(self.observer2)
        self.observable.register(self.observer3)

        self.observable.unregister_all()

        # Should be zero registered
        self.assertEqual(self.observable.count(), 0)

    def test_register(self):
        self.observable.register(self.observer1)
        self.observable.register(self.observer2)
        self.observable.register(self.observer3)

        # Should be three registered
        self.assertEqual(self.observable.count(), 3)
        self.observable.unregister_all()

    def test_unregister(self):
        self.observable.register(self.observer1)
        self.observable.register(self.observer2)
        self.observable.register(self.observer3)

        self.observable.unregister(self.observer2)
        self.observable.unregister(self.observer3)

        # Should be one registered
        self.assertEqual(self.observable.count(), 1)
        self.observable.unregister_all()

    def test_update_observers(self):
        self.observable.register(self.observer1)

        self.observable.update_observers('abc', msg='123')
        self.assertEqual(self.observer1.args[0], 'abc')
        self.assertEqual(self.observer1.kwargs['msg'], '123')
        self.observable.unregister_all()

    def test_type_handler(self):
        self.assertIsNone(self.observable.register(self.observer1))
        self.assertIsNone(self.observable.register(self.observer1.update))
        self.assertIsNone(self.observable.register(AnObserver()))

        error_msg = 'This is not a class-object, method or function'

        with self.assertRaisesRegex(TypeError, error_msg):
            self.observable.register(self.observer1.update())
        with self.assertRaisesRegex(TypeError, error_msg):
            self.observable.register(an_function())
        with self.assertRaisesRegex(TypeError, error_msg):
            self.observable.register(None)

        with self.assertRaisesRegex(TypeError, error_msg):
            self.observable.register(AnClass())
        with self.assertRaisesRegex(TypeError, error_msg):
            self.observable.register(AnClass)
        with self.assertRaisesRegex(TypeError, error_msg):
            self.observable.register(AnObserver)

        with self.assertRaisesRegex(TypeError, error_msg):
            self.observable.register(AnClass.update)


if __name__ == "__main__":
    unittest.main()
