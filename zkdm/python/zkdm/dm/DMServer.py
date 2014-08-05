# coding: utf-8

from tornado.web import RequestHandler, Application, url
from tornado.ioloop import IOLoop
import ServicesManager


# DM Service 端口
DMS_PORT = 10000

# 服务管理器，何时 close ??
_sm = ServicesManager.ServicesManager()


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
		if oper == 'start':
			if _sm.start_service(name):
				result = { 'result':'ok', 'info':'started' }
			else:
				result = { 'result':'error', 'info':'not found or disabled' }
		elif oper == 'stop':
			if _sm.stop_service(name):
				result = { 'result':'ok', 'info':'stopped' }
			else:
				result = { 'result':'error', 'info':'not found or disabled' }
		elif oper == 'disable':
			_sm.enable_service(name, False)
			result = { 'result': 'ok', 'info':'disabled' }
		elif oper == 'enable':
			_sm.enable_service(name, True)
			result = { 'result': 'ok', 'info':'enabled' }
		else:
			result = { 'result':'error', 'info':'unknown operator' }
		
		self.write(result)



class ListServiceHandler(RequestHandler):
	''' 返回服务列表 '''
	def get(self):
		ss = _sm.list_services()
		ssd = { 'type':'list', 'data':ss }
		result = { 'result':'ok', 'info':'', 'value':ssd }
		self.write(result)


def make_app():
	return Application([
			url(r'/dm/help', HelpHandler),
			url(r'/dm/list', ListServiceHandler),
			url(r'/dm/([^/]+)/(.*)', ServiceHandler),
			])




if __name__ == '__main__':
	app = make_app()
	app.listen(DMS_PORT)
	IOLoop.instance().start()


