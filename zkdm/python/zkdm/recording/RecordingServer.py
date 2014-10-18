# coding: utf-8

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import socket

from tornado.options import define, options
from tornado.web import RequestHandler, Application, url
from RecordingCommand import RecordingCommand

define("port", default=10007, help="run on the given port", type=int)

def _param(req, key):
    if key in req.request.arguments:
        return req.request.arguments
    else:
        return None

_rcmd = None

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Use the /recording/help for more help !")

class HelpHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('help.html')

class CmdHandler(tornado.web.RequestHandler):
    def get(self):
        rc={}
        rc['result']='ok'
        rc['info']=''

        cmd = _param(self, 'RecordCmd')

        if cmd is None:
            cmd = _param(self,'MetaInfoCmd')

        if cmd is None:
            cmd = _param(self,'BroadCastCmd')

        if cmd is None:
            rc['result'] = 'err'
            rc['info'] = '"RecordCmd" MUST be supplied!'
            self.write(rc)
            return


        else:
            args = (self.request.uri.split('?'))[1]
            rc=_rcmd.send_command(args)
            self.write(rc)

        return


def main():

    tornado.options.parse_command_line()
    application = tornado.web.Application([
        url(r"/", MainHandler),
        url(r"/recording/cmd",CmdHandler),
        url(r"/recording/help", HelpHandler),
    ])

    global _rcmd
    _rcmd = RecordingCommand()

    application.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
