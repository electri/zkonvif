# coding: utf-8

from tornado.web import Application,RequestHandler,url
from tornado.ioloop import IOLoop


def _param(req, key):
	if key in req.request.arguments:
		return req.request.arguments[key][0]
	else:
		return None
		


class HostUtilsHandler(RequestHandler):
	''' 实现一组 host 相关的服务，如“关机” 等 ...
	'''
	def get(self):
		rc = { 'result': 'ok', 'info': '' }
		cmd = _param(self, 'command')
		if cmd is None:
			rc['result'] = 'err'
			rc['info'] = '"command" MUST be supplied!'
			self.write(rc)
			return

		if cmd == 'poweroff':
			pass

		if cmd == 'reboot':
			pass

		if cmd == 'stat':
			pass



_ioloop = None

class InternalHandler(RequestHandler):
	def get(self):
		rc = {}
		rc['result'] = 'ok'
		rc['info'] = ''

		cmd = _param(self, 'command')

		if cmd is None:
			rc['result'] = 'err'
			rc['info'] = '"command" MUST be suppiled!'
			self.write(rc)
			return

		if cmd == 'exit':
			global _ioloop
			rc['info'] = 'exit!!!'
			self.write(rc)
			_ioloop.stop()

		if cmd == 'version':
			rc['result'] = 'err'
			rc['info'] = 'now, the version command NOT supported!!!'
			self.write(rc)

		

def main():
	app = Application([
			url(r'/host/util', HostUtilsHandler),
			url(r'/host/internal', InternalHandler)
			])
	app.listen(10004)
	global _ioloop
	_ioloop = IOLoop.instance()
	_ioloop.start()



if __name__ == '__main__':
	main()

