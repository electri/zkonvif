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
	def __init__(self, sv_urls, hb_list, mtx_reg, mtx_hb):
		threading.Thread.__init__(self)
		self.sv_urls_ = sv_urls
		self.hb_list_ = hb_list
		self.mtx_reg_ = mtx_reg
		self.mtx_hb_ = mtx_hb
		
	def run(self):
		while True:
			temp_urls = [] 
			self.mtx_.acquire()
			for e in self.sv_urls_:
				f = urllib2.openurl(e + r'/internal/is_prepared')
				jv = f.read(100)
				dv = json.loads(jv)
				if dv['result'] is 'ok':
					f = urllib2.openurl(e + r'/internal/get_all_service')
					jv = f.read(100)
					dv = json.loads(jv)
					for e1 in dv['sevices']:
						register(e1)
						heatbeat(e1)
						self.mtx_hb_.acquire()
						self.hb_list_.append(e1)
						self.mtx_hb_.release()
				else:
					temp_urls.append(e)
			self.sv_urls_ = {}
			for e in temp_urls_:
				self.sv_urls_.append(e)
			self.mtx_.release()			

class HeartBeatClass(threading.Thread):
	def __init__(self, hb_list, mtx_hb):
		threading.Thread.__init__(self)
		self.hb_list_ = hb_list
		self.mtx_hb_ = mtx_hb
		
	def run(self):
		while True:
			self.mtx_hb_.acquire()		
			for e in self.hb_list_:
				heartBeat(e)
			self.mtx_hb_.release()

_client_vector = []
hb_background = HeartBeatClass(_client_vector)

hb_background.start()

_client_params = get_ipconfig()
def reg_service(sip, sport, client_type,client_id):
	info = {'sip':sip, 'sport':sport, 'type':client_type, 'id':client_id, 'url':'123'}
	_client_params.update(info)
	reg = RegClass(_client_params, _client_vector)
	reg.start()
