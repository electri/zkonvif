from tornado import *
import regHb
import json
#with open('c:\...','r') as f:
#	d1 = json.load(f)
#   json.dump(disc, f)
class Application(requestion):
	def __init__(self, url, port)
		requestion.__init__(self)
		self.url = url
		self.port = port
		self.action = 'defualt'
	def response(self):
		if self.message is 'help':
			self.write('./help.html')
		else if 'ptz':
			if self.action is 'start'
				execfile('../ptz/PtzServer.py')
#FIXME: id,譬如ptz的teacher,student,必须给出
				regHa.reg_service(url, port,self.message,id)
#可以传递参数 os.system('../ptz/PtzServer.py')
#可以获得文件输出 os.popen('../ptz/PtzServer.py')
#FIXME:port_string需要想办法获取;若在本程序中关闭则不用
			if self.action is 'close'
				#TODO:不要忘记删除文件,这些完全可以放到内部解决
#delet('sms'+message+'.json')
				urllib2.open('http://127.0.0.1:' + port_string + '/' + message + '/' + action)
				


