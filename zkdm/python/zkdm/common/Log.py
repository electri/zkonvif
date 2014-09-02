# coding: utf-8

import urllib2
import json, time


class Log:
	''' 为了方便的使用 LogServer
	'''
	def __init__(self, project, base_url = None):
		self.__project = project
		if base_url is None:
			self.__base_url = 'http://localhost:10005/log'
		else:
			self.__base_url = base_url


	
	def log(self, content, level = 99):
		''' using PUT ....
			这么使用 urllib2，很神奇啊 ...
		'''
		opener = urllib2.build_opener(urllib2.HTTPHandler)
		req = urllib2.Request(self.__base_url + '/save', self.__build_body(level, content))
		req.add_header('Content-Type', 'application/json')
		req.get_method = lambda: 'PUT'
		print opener
		url = opener.open(req)

	
	def __build_body(self, level, content):
		''' 构造 json 数据，并返回,
			注意，字符串必须能够 json.loads()，要求使用双引号 
		'''
		data = {}
		data["project"] = self.__project
		data["level"] = level
		data["stamp"] = int(time.time())
		data["content"] = content

		# FIXME: 这种提供替换方式有问题，content 中可能有 .... 
		s = str(data).replace('\'', '\"')
		print s
		return s




if __name__ == '__main__':
	log = Log('testing')
	log.log('abcd')

