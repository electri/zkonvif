import sys, io, json, threading
import urllib2
import time

def get_utf8_body(req):
    body = ''
    b = req.read().decode('utf-8')
    while b:
        body += b
        b = req.read().decode('utf-8')
    return body

def reg(h_ip, h_mac, h_type, sip, sport):
    url = 'http://%s:%s/deviceService/regHost?mac=%s&ip=%s&hosttype=%s'%\
          (sip, sport, h_mac, h_ip, h_type)

    print 'reg: url', url
    s = None
    try:
        s = urllib2.urlopen(url)
    except Exception as e:
        print e
        return False
    ret = get_utf8_body(s)
    if u'ok' in ret:
        return True
    else:
        return False
        

def isMacList(url):
    print 'isMacList: calling ...'
    try:
        s = urllib2.urlopen(url)
    except Exception as e:
        return False

    ret = get_utf8_body(s)

    if ret is '':
        return False
    else:
        return True

    
class RegHost(threading.Thread):
    def __init__(self, _myip, _mac):
		self.isQuit = False
		self.myip = _myip
		self.mymac = _mac
		threading.Thread.__init__(self)
		
    def join(self):
        self.isQuit = True

    def run(self):
        host_type = None
        sip = None
        sport = None
        listByMacUrl = None
        try:
            f = io.open(r'../host/config.json', 'r', encoding='utf-8')
            s = json.load(f)
            host_type = s['host']['type']
            sip = s['regHbService']['sip']
            sport = s['regHbService']['sport']
            f.close()
        except Exception as e:
			print e
            rc['info'] = 'can\'t get host info'
            rc['result'] = 'err'
        listByMacUrl = r'http://%s:%s/deviceService/listByMac?Mac=%s'%(sip, sport, self.mymac)


        while True:
            while reg(self.myip, self.mymac, host_type, sip, sport) == False:
                time.sleep(5)

            time.sleep(10)

            while isMacList(listByMacUrl) == True:
                time.sleep(10)
 
