# coding: utf-8

import urllib, os, time
from suds.client import Client

class WsdlLoader:
	def __init__(self, wsdl_filename, soap_endp = ""):
		''' 加载本地 wsdl 文件 '''
		url = 'file://' + urllib.pathname2url(os.path.abspath(wsdl_filename))
		self.__client = Client(url)
		self.__client.set_options(location = soap_endp)
		print soap_endp


	def client(self):
		return self.__client

	
	def service(self):
		return self.__client.service


	def factory(self):
		return self.__client.factory




if __name__ == '__main__':
	ss = WsdlLoader('./wsdl/zkreg.wsdl', 'http://172.16.1.14:8877')
	s = ss.service()
	c = ss.client()
	print c
