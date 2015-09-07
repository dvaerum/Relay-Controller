import os
from tornado.websocket import WebSocketHandler, tornado
from tornado.escape import json_encode
from lib.log import logger
from lib.observer import Observer
from tornado.web import RequestHandler, url

from lib import network_api
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
    def __init__(self, webapps_path):
        handlers = [
            url(r"/log/", LogHandler, name="log"),
            url(r"/log_socket/", LogSocketHandler, name="log_socket"),
        ]
        settings = dict(
            # cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            template_path=webapps_path,
            static_path=os.path.join(webapps_path, "static"),
            # xsrf_cookies=True,
            debug=False,
        )
        tornado.web.Application.__init__(self, handlers, **settings)