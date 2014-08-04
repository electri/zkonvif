# coding: utf-8

from WsdlLoader import WsdlLoader
import threading, time


REG_ENDP = 'http://172.16.1.103:8899'


class __HBWorking(threading.Thread):
	''' 心跳工作线程, 周期心跳 ....
	'''
	def __init__(self):
		threading.Thread.__init__(self)
		self.daemon = True	# 为了无条件结束 ...
		self.__wsdl = WsdlLoader('wsdl/zkreg.wsdl', REG_ENDP)
		self.__service = self.__wsdl.service()
		self.__mutex = threading.RLock()
		self.__tokens = [] # 存储 regservice 返回的 token


	def add(self, token):
		self.__mutex.acquire()
		self.__tokens.append(token)
		self.__mutex.release()


	def remove(self, token):
		self.__mutex.acquire()
		self.__tokens.remove(token)
		self.__mutex.release()


	def run(self):
		while True:
			time.sleep(10.0)
			self.__mutex.acquire()
			for token in self.__tokens:
				self.__hb(token)
			self.__mutex.release()


	def __hb(self, t):
		''' 执行心跳 '''
		self.__service.heartBeat(t)
		


_thread_run = None


def getThread():
	global _thread_run
	if _thread_run:
		return _thread_run
	else:
		_thread_run = __HBWorking()
		_thread_run.start()
		return _thread_run



class zkRegProxy:
	''' 将服务注册到传统的 mse 模型 ...
		通过工作线程, 实现心跳
	'''
	def __init__(self, service_name, service_type, service_url, service_version):
		self.__service_name = service_name
		self.__service_type = service_type
		self.__service_url = service_url
		self.__service_version = service_version
		self.__token = None

	
	def reg(self):
		wsdl = WsdlLoader("wsdl/zkreg.wsdl", REG_ENDP)
		sd = wsdl.factory().create('Service')
		sd.name = self.__service_name
		sd.catalog = wsdl.factory().create('zkreg:Catalog').Service
		sd.hostname = ''
		sd.type = self.__service_type
		sd.parent = ''
		sd.version = self.__service_version
		sd.showname = ''
		sd.urls = wsdl.factory().create('zkreg:Urls')
		sd.urls.item.append(self.__service_url)
		token = wsdl.service().regService(sd)
		print token
		self.__token = token
		getThread().add(self.__token)


	def unreg(self):
		if self.__token:
			getThread().remove(self.__token)
			wsdl = WsdlLoader('wsdl/zkreg.wsdl', REG_ENDP)
			wsdl.service().unregService(self.__token);
			self.__token = None



if __name__ == '__main__':
	reg = zkRegProxy('test_service_name', 'test', 'test://172.16.1.116', '0.0')
	reg.reg()
	time.sleep(30.0)
	reg.unreg()
