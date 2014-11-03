import sys
import json
import time
sys.path.append('../')
from common.utils import zkutils

HB_TIME = 10

def getRgHbSv(f):
    return json.load(f, 'utf-8')['regHbService'] 

def getLocalHost():
    localIp = zkutils.myRealip()
    localMac = zkutils.myMac()
    localHost = {}
    localHost['localIp'] = localIp
    localHost['localMac'] = localMac
    return localHost

import urllib2

def getUrl(client_params, fun_str):
	v =	client_params
	ret = 'http://' + v['sip'] + ':' + v['sport'] + '/' + fun_str + '=' +v['ip'] + '_' + v['mac'] + '_' + v['type'] + '_' + v['id'] + '_' + v['url']
	print ret
	return ret

def register(client_params):
	regUrl = getUrl(client_params, 'deviceService/registering?serviceservice_')
	s = urllib2.urlopen(regUrl)
	ret = s.read(100)
	v = client_params['ip'] + '_' + client_params['mac'] + '_' + client_params['type' + '_' + 'id'

	if v in ret:
		return True
	else:
		return False

def heatbeat(service_params):
	heartBeatUrl = get_url(service_params, 'deficeService/heartbeat?serviceservice_')
	s = urllib2.urlopen(heartBeatUrl)
	ret = s.read(100)	

import threading


class RegClass(threading.Thread):
	def __init__(self, pcs_paras, services, mtx_reg, mtx_hb):
		threading.Thread.__init__(self)
		self.pcs_paras_ = pcs_paras
		self.services_ = services
		self.mtx_reg_ = mtx_reg
		self.mtx_hb_ = mtx_hb
        self.service_ = {}
        self.service_.update(getRgHbSv('config.json'))
        self.service_.update(getLocalHost())
def run(self):
		while True:
			temp_urls = [] 
			self.mtx_.acquire()
			for e in self.pcs_paras_:
                self.service_.update(e)
				f = urllib2.openurl(e['url'] + r'/internal/get_all_service')
				jv = f.read(1000)
				dv = json.loads(jv, 'utf-8')
				if dv['state'] is 'competed':
    				for e1 in dv['ids']:
                        isReg = False
                        self.service_['id'] = e1
                        while not isReg:
						    if register(self.service_) is 'ok':
                                isReg = True
						heatbeat(e1)
						self.mtx_hb_.acquire()
						self.services_.append(self.service_)
						self.mtx_hb_.release()
				    self.pcs_paras_.remove(e)
			self.mtx_.release()			

class HbClass(threading.Thread):
	def __init__(self, services, mtx_hb):
		threading.Thread.__init__(self)
		self.services_ = services
		self.mtx_hb = mtx_hb
		
	def run(self):
		while True:
			self.mtx_hb_.acquire()		
			for e in self.services_:
				heartBeat(e)
			self.mtx_hb_.release()
            time.sleep(HB_TIME)
