import inspect

__author__ = 'alt_mulig'
__doc__ = "http://www.giantflyingsaucer.com/blog/?p=5117"


class Observable(object):
    def __init__(self):
        self.__observers = []

    def register(self, observer):
        if observer not in self.__observers:
            # TODO: test if type None is accepted
            # TODO: test if the attr update is accepted if it is variable like "update = 4"
            if (hasattr(observer, "update") and inspect.ismethod(observer.update)) or inspect.ismethod(observer) or inspect.isfunction(observer):
                self.__observers.append(observer)
            else:
                raise TypeError("This is not a class-object, method or function")

    def unregister(self, observer):
        if observer in self.__observers:
            self.__observers.remove(observer)

    def unregister_all(self):
        if self.__observers:
            del self.__observers[:]

    def update_observers(self, *args, **kwargs):
        for observer in self.__observers:
            if hasattr(observer, "update"):
                observer.update(*args, **kwargs)
            else:
                observer(*args, **kwargs)

    def count(self):
        return len(self.__observers)
