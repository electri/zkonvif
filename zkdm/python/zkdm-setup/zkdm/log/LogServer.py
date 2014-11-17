# coding: utf-8


from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application, url
from dbhlp import DBHlp
import time, json
import sys

sys.path.append('../')
from common.reght import RegHt
VERSION = 0.9
VERSION_INFO = 'Log Service ...'


class SaveHandler(RequestHandler):
	''' 保存 

			支持 GET/PUT 两种方式, GET 支持短小的 content ...
			PUT 使用 Content-Type: application/json
	'''
	def get(self):
		p = self.request.arguments
		rc = {}
		rc['result'] = 'ok'
		rc['info'] = ''
		rc['value'] = {}

		if 'project' not in p:
			rc['result'] = 'err'
			rc['info'] = '"project" MUST be supplied!'
			self.write(rc)
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

		rc['info'] = 'log saved'
		self.write(rc)
		


	def put(self):
		print 'PUT ...'
		if 'Content-Type' not in self.request.headers:
			rc['result'] = 'err'
			rc['info'] = 'Content-Type: MUST be application/json'
			self.write(rc)
			return
		else:
			ct = self.request.headers.get('Content-Type')
			if ct.find('application/json') == -1:
				rc['result'] = 'err'
				rc['info'] = 'Content-Type: MUST be application/json'
				self.write(rc)
				return
			else:
				item = json.loads(self.request.body)
				if not self.__save(item):
					rc['result'] = 'err'
					rc['info'] = 'format err'
					self.write(rc)
					return
				else:
					rc['info'] = 'log saved'
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
		rc = {}
		rc['result'] = 'ok'
		rc['info'] = ''

		p = self.request.arguments
		print p
		project = self.__param('project', p)
		level = self.__param('level', p)
		stamp_begin = self.__param('stamp_begin', p)
		if stamp_begin is None:
			stamp_begin = str(time.time() - 60) # 缺省返回最近一分钟的日志
		stamp_end = self.__param('stamp_end', p)
		db = DBHlp()
		logs = db.query(project, level, stamp_begin, stamp_end)
		value = {}
		value['type'] = 'list'
		value['data'] = logs
		rc['value'] = value
		self.write(rc)


	def __param(self, key, params):
		if key in params:
			value = params[key]
			return value[0]
		return None


# 只是为了支持 internal?command=exit, 可以优雅的结束 ...
_ioloop = IOLoop.instance()
rh = RegHt('log', 'log', r'10005/log')


class InternalHandler(RequestHandler):
	''' 处理内部命令 '''
	def get(self):
		rc = {}
		rc['result'] = 'ok'
		rc['info'] = ''

		cmd = self.__param('command')
		if cmd is None:
			rc['result'] = 'err'
			rc['info'] = '"command" MUST be suppiled!'
			self.write(rc)
			return

		if cmd == 'version':
			ver = {}
			ver['version'] = VERSION
			ver['descr'] = VERSION_INFO
			data = {}
			data['type'] = 'version'
			data['data'] = ver
			rc['value'] = data
			self.write(rc)

		if cmd == 'exit':
			global _ioloop
			rc['info'] = 'exit!!!'
			rh.join()
			self.write(rc)
			_ioloop.stop()
		

	def __param(self, key):
		if key in self.request.arguments:
			return self.request.arguments[key][0]
		else:
			return None


def make_app():
	return Application([
			url(r'/log/save', SaveHandler),
			url(r'/log/query', QueryHandler),
			url(r'/log/help', HelpHandler),
			url(r'/log/internal', InternalHandler),
			])


def main():
	app = make_app()
	app.listen(10005)
	global _ioloop
	_ioloop.start()

	# 结束 ..
	print 'Log service end ...'



if __name__ == '__main__':
	main()

