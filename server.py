#!/usr/bin/env python
import os
import sys
import signal

from tornado.websocket import WebSocketHandler, tornado
from tornado.escape import json_encode
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application, url

from lib import network_api
from lib.log import logger
from lib.observer import Observer
from lib.server.server_api import server


__author__ = 'alt_mulig'


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
        logger.debug("WebSocket opened")
        self.write_message(json_encode({'COMMAND': network_api.COM_RELAY,
                                        'STATUS': network_api.STA_RELOAD,
                                        'DATA': server.get_relays()}))

    def on_message(self, message):
        # TODO: Send old data
        kilewatt, second = server.get_kilowatt()
        self.write_message(json_encode({"kilowatt": kilewatt,
                                        "second": second}))

    def on_close(self):
        LogSocketHandler.waiters.remove(self)
        logger.debug("WebSocket closed")


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

def signal_handler_sigterm(signal, frame):
    logger.info("Exiting...")
    IOLoop.current().stop()
    # keep_connected.stop()
    server.stop()


    logger.info("Exited")
    sys.exit(0)


def signal_handler_sigkill(signal, frame):
    pass


def main():
    app = Application()
    if len(sys.argv) == 4:
        app.listen(int(sys.argv[3]), address='')
    else:
        app.listen(8002, address='')
    server.start()
    server.observe_kW.register(LogSocketHandler)


    signal.signal(signal.SIGTERM, signal_handler_sigterm)
    signal.signal(signal.SIGHUP, signal_handler_sigkill)

    try:
        IOLoop.current().start()
    except KeyboardInterrupt:
        signal_handler_sigterm(None, None)


if __name__ == '__main__':
    main()
