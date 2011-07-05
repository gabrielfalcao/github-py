# #!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# <HTTPretty - HTTP client mock for Python>
# Copyright (C) <2011>  Gabriel Falcão <gabriel@nacaolivre.org>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
import os
import time

from tornado import autoreload
from tornado.web import Application
from tornado.web import RequestHandler
from tornado.ioloop import IOLoop
from github.tornado import authenticated
from multiprocessing import Process

from lettuce import before, after, world


class UserHandler(RequestHandler):
    @authenticated
    def get(self, api, name, params):
        self.write(api.user.raw)


class Server(object):
    is_running = False

    def __init__(self, port):
        self.port = int(port)
        self.process = None

    @classmethod
    def get_handlers(cls):
        return Application(
            [
                (r"/(.*)/?(.*)", UserHandler),
            ],
            github_client_id=world.tornado_app_id,
            github_client_secret=world.tornado_app_secret,
            cookie_secret=__file__,
        )

    def start(self, daemon=True):
        def go(app, port, data={}):
            app.listen(int(port))
            loop = IOLoop.instance()
            autoreload.start(loop)
            loop.start()

        app = self.get_handlers()

        data = {}
        args = (app, self.port, data)

        if daemon:
            self.process = Process(target=go, args=args)
            self.process.start()
            time.sleep(0.4)
        else:
            go(*args)

    def stop(self):
        try:
            os.kill(self.process.pid, 9)
        except OSError:
            self.process.terminate()
        finally:
            self.is_running = False

if __name__ == '__main__':
    print "Listening on http://localhost:9999/"
    Server(9999).start(daemon=False)


@before.each_scenario
def prepare_tornado(scenario):
    if 'tornado' in scenario.name.lower():
        world.server = Server(9999)
        world.server.start()


@after.each_scenario
def halt_tornado(scenario):
    if hasattr(world, 'server'):
        world.server.stop()
