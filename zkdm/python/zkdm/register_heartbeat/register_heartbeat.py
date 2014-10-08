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

def register(port, _type, _id, rets, disc):
	ipconfig = get_ipconfig()	
	disc = ipconfig
	regUrl = 'http://' + ipconfig['ip'] + ':' + port + 'deviceService/registering?serviceinfo=' + ipconfig['ip'] + '_' + ipconfig['mac'] +'_' + _type + '_' + _id +'_' + ipconfig['ip']
	ret = urllib2.urlopen(regUrl)
	s = ret.read(100)
	if s == rets:
		return True
	else:
		return False

def heatbeat(poet, _type, _id, rets, disc):
		ipconfg = get_ipconfg()
		disc =  

import threading

class RegClass(threading.Thread):
	def __init__(self, port, _type, _id, rets, vector):
		self.port = port
		self._type = _type
		self._id = _id
		self.rets = rets
		self.vector = vector
	
	def run(self):
		isquit = False
		disc = {}
		mutex = threading.Lock()
		while not isquit:
			if register(self.port, self._type, self._id, self.rets, disc)
				mutex.acquire()
				
				vector.add(disc)
	
				
