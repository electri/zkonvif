# coding: utf-8


from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application, url
from dbhlp import DBHlp
import time, json

class SaveHandler(RequestHandler):
	''' 保存 

			支持 GET/PUT 两种方式, GET 支持短小的 content ...
			PUT 使用 Content-Type: application/json
	'''
	def get(self):
		p = self.request.arguments

		if 'project' not in p:
			self.__my_err('"project" MUST be supplied!')
			return

		project = p['project'][0]

		if 'level' in p:
			level = int(p['level'][0])
		else:
			level = 99

		if 'stamp' in p:
			stamp = float(p['stamp'][0])
		else:
			stamp = time.time()

		if 'content' in p:
			content = p['content'][0]
		else:
			content = ''

		db = DBHlp()
		db.save(project, level, stamp, content)

		rc = { 'result':'ok', 'info':'log saved' }
		self.write(rc)
		


	def put(self):
		print 'PUT ...'
		if 'Content-Type' not in self.request.headers:
			self.__my_err('Content-Type: MUST be application/json')
		else:
			ct = self.request.headers.get('Content-Type')
			if ct.find('application/json') == -1:
				self.__my_err('Content-Type: MUST be application/json')
			else:
				print self.request.body
				print type(self.request.body)
				item = json.loads(self.request.body)
				print item
				if not self.__save(item):
					self.__my_err('format err')
				else:
					rc = { 'result':'ok', 'info':'log saved' }
					self.write(rc)


	
	def __my_err(self, info):
		rc = { 'result': 'err', 'info': info }
		self.write(rc)


	def __save(self, item):
		print item, type(item)
		if 'project' in item and 'level' in item and 'content' in item:
			if 'stamp' in item:
				stamp = item['stamp']
			else:
				stamp = int(time.time())
			db = DBHlp()
			db.save(item['project'], item['level'], stamp, item['content'])
			return True
		else:
			return False



class HelpHandler(RequestHandler):
	def get(self):
		self.render('help.html')



class QueryHandler(RequestHandler):
	''' 查询 '''
	def get(self):
		p = self.request.arguments
		print p
		project = self.__param('project', p)
		level = self.__param('level', p)
		stamp_begin = self.__param('stamp_begin', p)
		if stamp_begin is None:
			stamp_begin = str(time.time() - 60) # 缺省返回最近一分钟的日志
		stamp_end = self.__param('stamp_end', p)
		db = DBHlp()
		rc = db.query(project, level, stamp_begin, stamp_end)
		x = { 'result':'ok', 'info':'', 'value': { 'type': 'list',
			'data': rc } }
		self.set_header('Content-Type', 'application/json')
		self.write(x)


	def __param(self, key, params):
		if key in params:
			value = params[key]
			return value[0]
		return None


def make_app():
	return Application([
			url(r'/log/save', SaveHandler),
			url(r'/log/query', QueryHandler),
			url(r'/log/help', HelpHandler),
			])


def main():
	app = make_app()
	app.listen(10005)
	IOLoop.current().start()



if __name__ == '__main__':
	main()

