# coding: utf-8

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import socket

from tornado.options import define, options
from tornado.web import RequestHandler, Application, url
from LivingCommand import LivingCommand

define("port", default=10008, help="run on the given port", type=int)

def _param(req, key):
    if key in req.request.arguments:
        return req.request.arguments
    else:
        return None

_lcmd = None

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Use the /living/help for more help !")

class HelpHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('help.html')

class ListHandler(tornado.web.RequestHandler):
    def get(self):
        '''TODO...'''
        self.write("not support")

class CmdHandler(tornado.web.RequestHandler):
    def get(self):
        rc={}
        rc['result']='ok'
        rc['info']=''

        cmd = _param(self, 'BroadCastCmd')

        if cmd is None:
            rc['result'] = 'err'
	    rc['info'] = '"BroadCastCmd" MUST be supplied!'
            self.write(rc)
            return
        elif cmd['BroadCastCmd']==['StartBroadCast']:
            rc = _lcmd.start()
            self.write(rc)
        elif cmd['BroadCastCmd']==['StopBroadCast']:
            rc=_lcmd.stop()
            self.write(rc)
        elif cmd['BroadCastCmd']==['SetBroadCastProperty']:
            args = (self.request.uri.split('?'))[1]
            rc=_lcmd.property(args)
            self.write(rc)
        else:
            args = (self.request.uri.split('?'))[1]
            rc=_lcmd.property(args)
            self.write(rc)


def main():

    tornado.options.parse_command_line()
    application = tornado.web.Application([
        url(r"/", MainHandler),
    	url(r"/living/cmd",CmdHandler),
        url(r"/living/help", HelpHandler),
        ])

    global _lcmd
    _lcmd = LivingCommand()

    application.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
