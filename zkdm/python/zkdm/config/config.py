# coding:utf-8
import tornado.httpserver
import tornado.ioloop
import tornado.web
import json
import config_utils as cu
from tornado.options import define, options
import os, sys
import stdlib

define("port", default=8888, help="run on the given port", type = int)

class DefaltHandler(tornado.web.RequestHandler):
		def get(self, obj):
			pass
			
class ConfigHandler(tornado.web.RequestHandler):
	def get(self, fname, process):
		if process == "get_cfg":
			ret = cu.fn_config(fname, 'display')	
			self.set_header('Content-Type', 'application/json')
			jret = json.dumps(ret)
			self.set_header("Cache-control", "no-cache")
			self.write(jret)

		elif process == "reset":
			self.set_header('Content-Type', 'application/json')
			self.set_header("Cache-control", "no-cache")
			stdlib.send_udp_data("\x09\x01", "127.0.0.1")	
			ret = {"result":"", "info": ""}
			jret = json.dumps(ret)
			self.write(jret)

		else:
			self.render(process)

	def put(self, fname, process):
		if process == "save":
			ret = cu.fn_config(fname, 'save', self.request.body)
			self.set_header('Content-Type', 'application/json')
			jret = json.dumps(ret)
			self.set_header("Cache-control", "no-cache")
			self.write(jret)

def main():
	tornado.options.parse_command_line()
	application = tornado.web.Application([
		(r'/([^/]*)', DefaltHandler),
		(r'/config/([^/]*)/([^/]*)', ConfigHandler)
	])
	http_server = tornado.httpserver.HTTPServer(application)
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
	main()
