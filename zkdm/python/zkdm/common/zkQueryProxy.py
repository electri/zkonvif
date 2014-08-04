# coding: utf-8

from WsdlLoader import WsdlLoader


Q_ENDP = 'http://172.16.1.103:8899'


class zkQuery:
	''' 对mse模型中的 zkq 模块的访问'''
	def __init__(self, endp = Q_ENDP):
		self.__wsdl = WsdlLoader('wsdl/zkq.wsdl', endp)
		# print self.__wsdl.client()


	def getAllServices(self, offline = False):
		return self.__wsdl.service().getAllServices(offline)




if __name__ == '__main__':
	query = zkQuery()
	import time
	t1 = time.time()
	n = 1000
	while n > 0:
		query.getAllServices(offline = True)
		n -= 1
	t2 = time.time()
	print query.getAllServices()
	print 'using ', t2-t1, ' seconds'


