# coding: utf-8

from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application, url
from ctypes import *
import re, sys

sys.path.append('../')

from common.KVConfig import KVConfig
from PtzWrap import Ptz


def load_ptz_config(cfg, who):
	''' 加载云台配置 '''
	config = {}
	fname = cfg.get(who)
	if fname:
		c = KVConfig(fname)
		config['serial_name'] = c.get('serial_name', 'COMX')
		config['addr'] = c.get('addr', '1')
		config['ptz'] = Ptz()
		config['ptz'].open(config['serial_name'], int(config['addr']))
	return config;

# 加载全局配置 ...
_cfg = KVConfig('ptz.config')
_config = {}
_config['teacher'] = load_ptz_config(_cfg, 'teacher')
_config['student'] = load_ptz_config(_cfg, 'student')


class HelpHandler(RequestHandler):
	def get(self):
		self.render('help.html')


class GetConfigHandler(RequestHandler):
	''' 返回云台配置 '''
	def get(self, path):
		cfg = self.__load_config()
		self.write(cfg)

	def __load_config(self):
		return {'ptzs': _config.keys() }


class ControllingHandler(RequestHandler):
	''' 处理云台操作 '''
	def get(self, sid, method):
		''' sid 指向云台，method_params 为 method?param1=value1&param2=value2& ....
		'''
		ret = self.__exec_ptz_method(sid, method, self.request.arguments)
		self.write(ret)

	def __exec_ptz_method(self, sid, method, params):
		if sid in _config:
			return _config[sid]['ptz'].call(method, params)
		else:
			return {'result':'error', 'info':'sid='+sid+' NOT found'}


def make_app():
	return Application([
			url(r'/help', HelpHandler),
			url(r"/config(/?)", GetConfigHandler),
			url(r'/ptz/([^\/]+)/([^\?]+)', ControllingHandler),
			])


def main():
	app = make_app()
	app.listen(10003)
	IOLoop.current().start()


if __name__ == '__main__':
	main()

