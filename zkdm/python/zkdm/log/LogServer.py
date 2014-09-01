# coding: utf-8


from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application, url
from dbhlp import DBHlp
import time

class SaveHandler(RequestHandler):
	''' 保存 

			支持 GET/PUT 两种方式, GET 支持短小的 content ...
			PUT 使用 Content-Type: application/json
	'''
	def get(self):
		pass


	def put(self):
		pass



class QueryHandler(RequestHandler):
	''' 查询 '''
	def get(self):
		p = self.request.arguments
		db = DBHlp()
		project = self.__param('project', p)
		level = self.__param('level', p)
		stamp_begin = self.__param('stamp_begin', p)
		if stamp_begin is None:
			stamp_begin = str(time.time() - 60) # 缺省返回最近一分钟的日志
		stamp_end = self.__param('stamp_end', p)
		rc = db.query(project, level, int(stamp_begin), stamp_end)
		x = { 'result':'ok', 'info':'', 'value': { 'type': 'list',
			'data': rc } }
		self.set_header('Content-Type', 'application/json')
		self.write(x)


	def __param(self, key, params):
		value = None
		if key in params:
			value = params[key]
		return value[0]


def make_app():
	return Application([
			url(r'/log/save', SaveHandler),
			url(r'/log/query', QueryHandler),
			])


def main():
	app = make_app()
	app.listen(10005)
	IOLoop.current().start()



if __name__ == '__main__':
	main()

