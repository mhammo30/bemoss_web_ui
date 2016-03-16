# -*- coding: utf-8 -*-
'''
Copyright (c) 2016, Virginia Tech
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
 following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those of the authors and should not be
interpreted as representing official policies, either expressed or implied, of the FreeBSD Project.

This material was prepared as an account of work sponsored by an agency of the United States Government. Neither the
United States Government nor the United States Department of Energy, nor Virginia Tech, nor any of their employees,
nor any jurisdiction or organization that has cooperated in the development of these materials, makes any warranty,
express or implied, or assumes any legal liability or responsibility for the accuracy, completeness, or usefulness or
any information, apparatus, product, software, or process disclosed, or represents that its use would not infringe
privately owned rights.

Reference herein to any specific commercial product, process, or service by trade name, trademark, manufacturer, or
otherwise does not necessarily constitute or imply its endorsement, recommendation, favoring by the United States
Government or any agency thereof, or Virginia Tech - Advanced Research Institute. The views and opinions of authors
expressed herein do not necessarily state or reflect those of the United States Government or any agency thereof.

VIRGINIA TECH – ADVANCED RESEARCH INSTITUTE
under Contract DE-EE0006352

#__author__ = "BEMOSS Team"
#__credits__ = ""
#__version__ = "2.0"
#__maintainer__ = "BEMOSS Team"
#__email__ = "aribemoss@gmail.com"
#__website__ = "www.bemoss.org"
#__created__ = "2014-09-12 12:04:50"
#__lastUpdated__ = "2016-03-14 11:23:33"

'''

import json
from zmq.eventloop import ioloop

ioloop.install()
from zmq.eventloop.zmqstream import ZMQStream
import zmq
import os
import sys
sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)).replace('/run', ''))
print sys.path
from tornado import websocket
from tornado import web
from _utils import messages as _
from settings_tornado import PROJECT_DIR
from tornado.options import options, define
import django.core.handlers.wsgi
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.wsgi
import os
import getpass

ctx = zmq.Context()

current_path = PROJECT_DIR
current_path = current_path.replace("/workspace/bemoss_web_ui", "")
print current_path

push_socket = "ipc://" + current_path + "/.volttron/run/publish"
sub_socket = "ipc://" + current_path + "/.volttron/run/subscribe"
print push_socket
print sub_socket

define('port', type=int, default=8082)
define('host', type=str, default="localhost")


def main():

    print os.path.expanduser("~")
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings_tornado'
    wsgi_app = tornado.wsgi.WSGIContainer(django.core.handlers.wsgi.WSGIHandler())
    tornado_app = tornado.web.Application(
        [
            (r"/socket_thermostat", ThermostatEventHandler),
            (r"/socket_rtu", RTUEventHandler),
            (r"/socket_vav", VAVEventHandler),
            (r"/socket_plugload", PlugLoadEventHandler),
            (r"/socket_lighting", LightingEventHandler),
            (r"/socket_misc", BemossMiscHandler),
            (r"/socket_identify", BemossIdentifyHandler),
            (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': PROJECT_DIR +
                                                                      "/static/"}),
            ('.*', tornado.web.FallbackHandler, dict(fallback=wsgi_app)),
        ])
    server = tornado.httpserver.HTTPServer(tornado_app)
    server.listen(options.port)
    print _.SERVER_STARTUP.format(options.host, options.port)
    tornado.ioloop.IOLoop.instance().start()


class WebHandler(web.RequestHandler):
    def get(self):
        pass

class MainHandler(websocket.WebSocketHandler):
    _first = True

    @property
    def ref(self):
        return id(self)

    def initialize(self):
        print 'Initializing tornado websocket'
        self.push_socket = ctx.socket(zmq.PUSH)
        self.sub_socket = ctx.socket(zmq.SUB)

        self.push_socket.connect(push_socket)
        self.sub_socket.connect(sub_socket)
        self.zmq_subscribe()

        self.zmq_stream = ZMQStream(self.sub_socket)
        self.zmq_stream.on_recv(self.zmq_msg_recv)

    def check_origin(self, origin):
        return True

    def open(self, *args, **kwargs):
        self.write_message("WebSocket opened from server")

    def on_message(self, message):
        if self._first:
            msg = {'message': message, 'id':self.ref, 'action':'connect'}
            print 'in if part - tornado server'
            self._first = False

        else:
            msg = {'message': message, 'id':self.ref, 'action':'message'}
            print 'in else part - tornado server'
            print msg

        self.write_message(msg)

    def on_close(self):
        self.write_message("WebSocket closed")
        msg = {'message': '', 'id': id(self), 'action': 'close'}
        try:
            self.write_message(msg)
        except:
            print "ui on_close write_message error exception"

    def zmq_msg_recv(self, data):
        print data
        zmessage = {'topic': '', 'headers': {}, 'message': ''}
        for item in data:
            if '/agent/ui' in item:
                zmessage['topic'] = item
            elif 'Date' in str(item):
                mesg = json.loads(item)
                zmessage['headers'] = mesg
            else:
                if '[' in item:
                    item = eval(item)
                    print type(item)
                    item = item[0]
                    if item[0] == '{':
                        item = json.loads(item)
                    zmessage['message'] = item
                else:
                    zmessage['message'] = item

        self.write_message(zmessage)

    def zmq_subscribe(self):
        self.sub_socket.setsockopt(zmq.SUBSCRIBE, "")


class ThermostatEventHandler(MainHandler):

    def zmq_subscribe(self):
        self.sub_socket.setsockopt(zmq.SUBSCRIBE, '/agent/ui/thermostat/')


class RTUEventHandler(MainHandler):

    def zmq_subscribe(self):
        self.sub_socket.setsockopt(zmq.SUBSCRIBE, '/agent/ui/rtu/')


class VAVEventHandler(MainHandler):

    def zmq_subscribe(self):
        self.sub_socket.setsockopt(zmq.SUBSCRIBE, '/agent/ui/vav/')


class PlugLoadEventHandler(MainHandler):

    def zmq_subscribe(self):
        self.sub_socket.setsockopt(zmq.SUBSCRIBE, '/agent/ui/plugload/')


class LightingEventHandler(MainHandler):

    def zmq_subscribe(self):
        self.sub_socket.setsockopt(zmq.SUBSCRIBE, '/agent/ui/lighting/')

class BemossMiscHandler(MainHandler):

    def zmq_subscribe(self):
        self.sub_socket.setsockopt(zmq.SUBSCRIBE, '/agent/ui/misc/')

class BemossIdentifyHandler(MainHandler):
    def zmq_subscribe(self):
        self.sub_socket.setsockopt(zmq.SUBSCRIBE, '/agent/ui/identify_response/')


application = web.Application([
    (r"/", WebHandler),
    (r"/socket_thermostat", ThermostatEventHandler),
    (r"/socket_rtu", RTUEventHandler),
    (r"/socket_vav", VAVEventHandler),
    (r"/socket_plugload", PlugLoadEventHandler),
    (r"/socket_lighting", LightingEventHandler),
    (r"/socket_misc", BemossMiscHandler),
    (r"/socket_identify", BemossIdentifyHandler),
])


if __name__ == "__main__":
    tornado.options.parse_command_line()
    main()
