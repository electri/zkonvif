import sys
import json
import time
sys.path.append('../')
from common.utils import zkutils

HB_TIME = 10

def getRgHbSv(f):
    return json.load(f) 

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


class RegClass(threading.Thread):
	def __init__(self, sv_urls, hb_list, mtx_reg, mtx_hb):
		threading.Thread.__init__(self)
		self.sv_urls_ = sv_urls
		self.hb_list_ = hb_list
		self.mtx_reg_ = mtx_reg
		self.mtx_hb_ = mtx_hb
        self.info = {}
        self.info.update(getRgHbSv('config.json'))
        self.info.update(getLocalHost())

	def run(self):
		while True:
			temp_urls = [] 
			self.mtx_.acquire()
			for e in self.sv_urls_:
				f = urllib2.openurl(e + r'/internal/get_all_service')
				jv = f.read(1000)
				dv = json.loads(jv)
				if dv['state'] is 'competed':
					dv = json.loads(jv)
                    self.info['type'] = dv['type']
                    self.info['url'] = dv['url']

					for e1 in dv['types']:
                        isReg = False
                        self.info['type'] = e1
                        while not isReg:
						    if register(self.info) is 'ok':
                                isReg = True
						heatbeat(e1)
						self.mtx_hb_.acquire()
						self.hb_list_.append(self.info)
						self.mtx_hb_.release()
				    self.sv_urls_.remove(e)
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
            time.sleep(HB_TIME)
