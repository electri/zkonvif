# coding: utf-8


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

        s = None
        try:
            s = urllib2.urlopen(url)
        except Exception as e:
            print e
            return False
        ret = get_utf8_body(s)
        if 'ok' in ret:
            return True
        else:
            return False
            

    def isGetMacList(sip, sport, mymac):
        url = r'http://%s:%s/deviceService/listByMac?mac=%s'%(sip, sport, self.mymac)
        try:
            s = urllib2.urlopen(url)
        except Exception as e:
            print e
            return False

        ret = get_utf8_body(s)
        l = len(ret)
        if l > 10:
            l = 10
        to_show = ret[0:l]
        if to_show == '':
            print '"*************************' + to_show + '"'
        else:
            print '"' + to_show + '"'

        if ret is '':
            return False
        else:
            return True

        
    class RegHost(threading.Thread):
        def __init__(self, _myip, _mac):
        self.isQuit = False
        self.event = threading.Event() 
        self.myip = _myip
        self.mymac = _mac
        threading.Thread.__init__(self)
        
    def join(self):
        self.isQuit = True
        self.event.set()

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

        while not self.isQuit:
            while not self.isQuit or reg(self.myip, self.mymac, host_type, sip, sport) == False:
                self.event.wait(5)

            self.event.wait(10)

            while isGetMacList(sip, sport, self.mymac) == True:
                self.event.wait(10)
 
