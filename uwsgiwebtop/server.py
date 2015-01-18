import time
import os
import json

import cherrypy
from cherrypy.process.plugins import Monitor
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import EchoWebSocket, WebSocket

from uwsgiwebtop import utils

assetsdir = os.path.join(os.path.dirname(__file__), 'assets')

SUBSCRIBERS = set()

class DataUpdateSocket(WebSocket):
    def __init__(self, *args, **kwargs):
        super(DataUpdateSocket, self).__init__(*args, **kwargs)
        SUBSCRIBERS.add(self)

    def close(self, code, reason=None):
        SUBSCRIBERS.remove(self)


def refresh_top_data():
    data = list(utils.collect_stats())
    text = json.dumps(data, indent=2, sort_keys=True)
    for s in SUBSCRIBERS:
        s.send(text)


class Root(object):
    @cherrypy.expose
    def index(self):
        with open(os.path.join(assetsdir, "index.html")) as f:
            return f.read()

    @cherrypy.expose
    def ws(self):
        handler = cherrypy.request.ws_handler


def run_server(host='0.0.0.0', port=8088):

    cherrypy.config.update({'server.socket_port': port,
                            'server.socket_host': host,
                            })
    WebSocketPlugin(cherrypy.engine).subscribe()
    cherrypy.tools.websocket = WebSocketTool()
    Monitor(cherrypy.engine, refresh_top_data, 1).subscribe()

    wsconf = {'tools.websocket.on': True,
              'tools.websocket.handler_cls': DataUpdateSocket,
              }
    staticconf = {'tools.staticdir.on': True,
                  'tools.staticdir.dir': assetsdir}
    cherrypy.quickstart(Root(), '/', config={'/ws': wsconf,
                                             '/static': staticconf})

if __name__ == '__main__':
    run_server()
