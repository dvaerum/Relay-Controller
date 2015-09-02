from queue import Queue
from selectors import DefaultSelector
from multiprocessing import Lock

__author__ = 'alt_mulig'


class SyncSelector(DefaultSelector):
    __selector_queue = Queue()
    __lock = Lock()

    def register(self, conn, event, data=None):
        self.__selector_queue.put((conn, event, data, True))
        self.__run()

    def unregister(self, conn):
        self.__selector_queue.put((conn, None, None, False))
        self.__run()

    def __run(self):
        if self.__lock.acquire(False):
            while not self.__selector_queue.empty():
                conn, event, data, do = self.__selector_queue.get()
                if do:
                    try:
                        super().unregister(conn)
                    except KeyError:
                        pass
                    finally:
                        super().register(conn, event, data)
                else:
                    super().unregister(conn)
            self.__lock.release()
