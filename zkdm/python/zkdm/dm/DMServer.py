# coding: utf-8

from tornado.web import RequestHandler, Application, url
from tornado.ioloop import IOLoop
import ServicesManager


# DM Service 端口
DMS_PORT = 10000
_sm = None # 在 main 中创建


class HelpHandler(RequestHandler):
	''' 提示信息 ....
	'''
	def get(self):
		self.render('./help.html')



class ServiceHandler(RequestHandler):
	''' 处理服务的控制命令 ....
		/dm/<service name>/<operator>?<params ...>
	'''
	def get(self, name, oper):
		rc = {}
		rc['result'] = 'ok'
		rc['info'] = ''

		if oper == 'start':
			if _sm.start_service(name):
				rc['info'] = 'started'
			else:
			 	rc['result'] = 'err'
			 	rc['info'] = 'not found or disabled'
		elif oper == 'stop':
			if _sm.stop_service(name):
				rc['info'] = 'stopped'
			else:
			 	rc['result'] = 'err'
			 	rc['info'] = 'not found or disabled'
		elif oper == 'disable':
			_sm.enable_service(name, False)
			rc['info'] = 'disabled'
		elif oper == 'enable':
			_sm.enable_service(name, True)
			rc['info'] = 'enabled'
		else:
			rc['info'] = 'unknown operator'
		
		self.write(rc)



class ListServiceHandler(RequestHandler):
	''' 返回服务列表 '''
	def get(self):
		rc = {}
		rc['result'] = 'ok'
		rc['info'] = ''

		ss = _sm.list_services()
		value = {}
		value['type'] = 'list'
		value['data'] = ss

		rc['value'] = value

		self.write(rc)


_ioloop = None # 全局，用于主动结束 ...


class InternalHandler(RequestHandler):
	def get(self):
		rc = {}
		rc['result'] = 'ok'
		rc['info'] = ''

		command = self.get_argument('command', 'nothing')
		if command == 'exit':
			rc['info'] = 'exit!!!'
			self.write(rc)
			global _ioloop
			_ioloop.stop()
		elif command == 'version':
			rc['info'] = 'now, not supported!!!'
			rc['result'] = 'err'
			self.write(rc)


def make_app():
	return Application([
			url(r'/dm/help', HelpHandler),
			url(r'/dm/list', ListServiceHandler),
			url(r'/dm/([^/]+)/(.*)', ServiceHandler),
			url(r'/dm/internal', InternalHandler),
			])




if __name__ == '__main__':

	# 服务管理器，何时 close ??
	_sm = ServicesManager.ServicesManager()
	app = make_app()
	app.listen(DMS_PORT)

	_ioloop = IOLoop.instance()
	_ioloop.start()

	# 此时，必定执行了 internal?command=exit，可以执行销毁 ...
	print 'DM end ....'
	_sm.close()

