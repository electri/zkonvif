# coding: utf-8

from tornado.web import Application,RequestHandler,url
from tornado.ioloop import IOLoop
from Stat import PerformanceMonitor


def _param(req, key):
	if key in req.request.arguments:
		return req.request.arguments[key][0]
	else:
		return None
		

_pm = None


class HelpHandler(RequestHandler):
	def get(self):
		self.render('help.html')



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
			self.__poweroff(rc)

		if cmd == 'reboot':
			self.__reboot(rc)

		if cmd == 'stat':
			if _pm is None:
				rc['result'] = 'err'
				rc['info'] = 'Unsupported for Performance Stats'
				self.write(rc)
			else:
				rc['value'] = { 'type': 'dict', 'data': _pm.get_all() }
				self.write(rc)


	def __poweroff(self, rc):
		rc['info'] = 'will poweroff atonce'
		self.write(rc)
		# TODO: 关机 ....


	def __reboot(self, rc):
		rc['info'] = 'will reboot atonce'
		self.write(rc)
		# TODO: 重启 ....



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
			url(r'/host/internal', InternalHandler),
			url(r'/host/help', HelpHandler),
			])
	app.listen(10004)

	global _pm
	_pm = PerformanceMonitor()
	_pm.start()

	global _ioloop
	_ioloop = IOLoop.instance()
	_ioloop.start()



if __name__ == '__main__':
	main()

