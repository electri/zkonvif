# coding: utf-8

from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application, url
from ctypes import *
import re, sys
import json, io, os
from PtzWrap import PtzWrap

sys.path.append("../")
from common.Log import Log
from common.reght import RegHt


# 从 config.json 文件中加载配置信息
# WARNING: 每次都配置文件时，都得注意工作目录的相对关系 ....
os.chdir(os.path.dirname(os.path.abspath(__file__)))


_all_config = json.load(io.open('./config.json', 'r', encoding='utf-8'))

def all_ptzs_config():
	''' 返回配置的云台 ... '''
	return _all_config['ptzs']
		
def load_ptz(config):
	''' 加载云台配置模块 '''
	ptz = {
		'name': config['name'],
		'serial': config['config']['serial'],
		'addr': config['config']['addr'],
		'ptz': None
	}
	print type(ptz['name'])
	print type(ptz['serial'])
	print type(ptz['addr'])
	print type(ptz['ptz'])
	if 'extent' in config['config']:
		ptz['cfgfile'] = config['config']['extent']

	# 此处打开 ...
	if True:
		is_ptz = False
		ptz['ptz'] = PtzWrap()
	 	# 来自 json 字符串都是 unicode, 需要首先转换为 string 交给 open 
		if 'cfgfile' in ptz:
			filename = ptz['cfgfile'].encode('ascii')
			print 'open with cfg:', filename
			is_ptz = ptz['ptz'].open_with_config(filename)
		else:
			print 'open ptz:', ptz['serial'], 'addr:', ptz['addr']
			is_ptz = ptz['ptz'].open(ptz['serial'].encode('ascii'), int(ptz['addr']))
		if not is_ptz:
			ptz['ptz'] = None	
	else:
		ptz['ptz'] = None
		print 'open failure'

	return ptz


def load_all_ptzs():
	''' 加载所有云台模块 '''
	ptzs = all_ptzs_config()
	ret = {}
	for x in ptzs:
		ret[x['name']] = (load_ptz(x))

	return ret


# 这里保存所有云台
_all_ptzs = load_all_ptzs()

rhs = []
stype = 'ptz'
for e in _all_ptzs:
	if _all_ptzs[e]['ptz'] is not None:
		sid = e
		rh = RegHt(stype, sid, sid)
		rhs.append(rh)	

class HelpHandler(RequestHandler):
	''' 返回 help 
		 晕啊，必须考虑当前目录的问题 ...
	'''
	def get(self):
		self.render('help.html')



class GetConfigHandler(RequestHandler):
	''' 返回云台配置 '''
	def get(self, path):
		cfg = self.__load_config()
		self.set_header('Content-Type', 'application/json')
		self.write(cfg)

	def __load_config(self):
		return { 'result':'ok', 'info':'', 'value': { 'type': 'list', 'data':all_ptzs_config() } }



class ControllingHandler(RequestHandler):
	''' 处理云台操作 '''
	def get(self, name, method):
		''' sid 指向云台，method_params 为 method?param1=value1&param2=value2& ....
		'''
		#log = Log('ptz')
		#log.log('name:' + name + ', method:' + method)

		ret = self.__exec_ptz_method(name, method, self.request.arguments)
		self.set_header('Content-Type', 'application/json')
		self.write(ret)

	def __exec_ptz_method(self, name, method, params):
		global _all_ptzs
		# print 'name:', name, ' method:', method, ' params:', params
		if name in _all_ptzs:
			if _all_ptzs[name]['ptz']:
				return _all_ptzs[name]['ptz'].call(method, params)
			else:
				return { 'result':'error', 'info':'ptz config failure' }
		else:
			return { 'result':'error', 'info':name + ' NOT found' }


# 为了支持 exit command
_ioloop = IOLoop.instance()


class InternalHandler(RequestHandler):
	def get(self):
		rc = {}
		rc['result'] = 'ok'
		rc['info'] = 'dispear'

		command = self.get_argument('command', 'nothing')
		print command
		if command == 'exit':
			rc['info'] = 'exit!!!'
			for e in rhs:
				e.join()
			global _ioloop
			_ioloop.stop()
			self.write(rc)
		elif command == 'version':
			rc['info'] = 'now version unsupported!!'
			rc['result'] = 'err'
			self.write(rc)

def make_app():
	return Application([
			url(r'/ptz/help', HelpHandler),
			url(r"/ptz/config(/?)", GetConfigHandler),
			url(r'/ptz/([^\/]+)/([^\?]+)', ControllingHandler),
			url(r'/ptz/internal', InternalHandler),
			])


def main():
	app = make_app()
	app.listen(10003)
	_ioloop.start()
	# 此时说明结束 ...
	print 'ptz service end ...'




if __name__ == '__main__':
	main()

