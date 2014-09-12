# coding: utf-8

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import socket

from tornado.options import define, options
from tornado.web import RequestHandler, Application, url
from RecordingCommand import RecordingCommand

define("port", default=8889, help="run on the given port", type=int)

def _param(req, key):
	if key in req.request.arguments:
		return req.request.arguments[key][0]
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

		cmd = _param(self, 'command')

		if cmd is None:
			rc['result'] = 'err'
			rc['info'] = '"command" MUST be supplied!'
			self.write(rc)
			return
		if cmd == 'start':
			_rcmd.start()

		if cmd=='pause':
			_rcmd.pause()

		if  cmd=='stop':
			_rcmd.stop()

		if cmd=='resume':
			_rcmd.resume()


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
