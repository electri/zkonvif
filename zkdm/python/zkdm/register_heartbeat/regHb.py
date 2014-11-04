import uuid
import socket


def get_ipconfig():
	ret = {}

	mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
	mac_str = ":".join([mac[e:e+2] for e in range(0,11,2)])
	ret['mac'] = mac_str

	fullHostName = socket.getfqdn(socket.gethostname())
	ret['hostname'] = fullHostName

	ip = socket.gethostbyname(fullHostName)
	ret['ip'] = ip
	return ret

import urllib2

def getUrl(client_params, fun_str):
	v =	client_params
	ret = 'http://' + v['sip'] + ':' + v['sport'] + '/' + fun_str + '=' +v['ip'] + '_' + v['mac'] + '_' + v['type'] + '_' + v['id'] + '_' + v['url']
	print ret
	return ret

def register(client_params):
	regUrl = getUrl(client_params, 'deviceService/registering?serviceinfo')
	s = urllib2.urlopen(regUrl)
	ret = s.read(100)
	v = client_params['ip'] + '_' + client_params['mac'] + '_' + client_params['type' + '_' + 'id'

	if v in ret:
		return True
	else:
		return False

def heatbeat(service_params):
	heartBeatUrl = get_url(service_params, 'deficeService/heartbeat?serviceinfo')
	s = urllib2.urlopen(heartBeatUrl)
	ret = s.read(100)	

import threading

_mutex = threading.Lock()

class RegClass(threading.Thread):
	def __init__(self, client_params, params_list):
		threading.Thread.__init__(self)
		self.client_params = {}
		self.client_params['sip'] = client_params['sip']
		self.client_params['sport'] = client_params['sport']
		self.client_params['ip'] = client_params['ip']
		self.client_params['mac'] = client_params['mac']
		self.client_params['id'] = client_params['id']
		self.client_params['url'] = client_params['url']
		self.client_params['type'] = client_params['type']
		print self.client_params 
		self.params_list = params_list
		self.quit_ = False	

	def run(self):
		register(self.client_params)
		while not self.quit_:
			if register(self.client_params):
				_mutex.acquire()
				heartBeat(self.client_params)
				self.params_list.add(self.client_params)
				self.quit_ = True
				_mutex.release()	

class HeartBeatClass(threading.Thread):
	def __init__(self, params_list):
		threading.Thread.__init__(self)
		self.params_list = params_list
		
	def run(self):
		while True:
			_mutex.acquire()		
			for e in self.params_list:
				heartBeat(e)
			_mutex.release()
		
_client_vector = []
hb_background = HeartBeatClass(_client_vector)

hb_background.start()

_client_params = get_ipconfig()
def reg_service(sip, sport, client_type,client_id):
	info = {'sip':sip, 'sport':sport, 'type':client_type, 'id':client_id, 'url':'123'}
	_client_params.update(info)
	reg = RegClass(_client_params, _client_vector)
	reg.start()
