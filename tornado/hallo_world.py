#!/usr/bin/env python
from socket import AF_INET, AF_UNIX
from threading import Thread
import threading
from time import sleep
import os
import sys
from lib import network_api

from tornado.websocket import WebSocketHandler, tornado
from tornado.escape import json_encode
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application, url

from lib.observer import Observer
from relay_net_client import Client

__author__ = 'alt_mulig'


def count_thread():
    while True:
        print("_____________________________________________")
        for t in threading.enumerate():
            print("Threads alive ({})".format(t.name))
        print("---------------------------------------------")
        sleep(1)
# Thread(target=count_thread, name="Count Thread").start()


class KeepConnected:
    __thread = None

    def __init__(self, family, address):
        self.client = Client(family, address)

    def start(self):
        if not self.__thread or not self.__thread.is_alive():
            self.__thread = Thread(target=self.__run, name="KeepConnected.__run()")
            self.__thread.start()
            self.client.observe_stop.register(self.start)

    def __run(self):
        while not self.client.is_connected():
            self.client.start()
            if self.client.is_connected():
                print("Connected to Server")
            else:
                print("Tries the connect again")
                sleep(1)

if len(sys.argv) == 3 or len(sys.argv) == 4:
    keep_connected = KeepConnected(family=AF_INET, address=(sys.argv[1], int(sys.argv[2])))
else:
    keep_connected = KeepConnected(family=AF_UNIX, address='/tmp/relay.sock')
client = keep_connected.client


class LogHandler(RequestHandler):
    def get(self):
        self.render("log.html")


class LogSocketHandler(WebSocketHandler, Observer):
    waiters = set()

    @classmethod
    def update(cls, data):
        for waiter in cls.waiters:
            waiter.write_message(json_encode(data))

    def open(self):
        LogSocketHandler.waiters.add(self)
        print("WebSocket opened")
        self.write_message(json_encode({'COMMAND': network_api.COM_RELAY,
                                        'STATUS': network_api.STA_RELOAD,
                                        'DATA': client.get_relays()}))

    def on_message(self, message):
        # TODO: Send old data
        kilewatt, second = client.get_kilowatt()
        self.write_message(json_encode({"kilowatt": kilewatt,
                                        "second": second}))

    def on_close(self):
        LogSocketHandler.waiters.remove(self)
        print("WebSocket closed")


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            url(r"/log/", LogHandler, name="log"),
            url(r"/log_socket/", LogSocketHandler, name="log_socket"),
        ]
        settings = dict(
            # cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            # template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            # xsrf_cookies=True,
            debug=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)


def main():
    app = Application()
    if len(sys.argv) == 4:
        app.listen(int(sys.argv[3]), address='')
    else:
        app.listen(8002, address='')
    keep_connected.start()
    keep_connected.client.observe_kW.register(LogSocketHandler)
    IOLoop.current().start()


if __name__ == '__main__':
    main()
