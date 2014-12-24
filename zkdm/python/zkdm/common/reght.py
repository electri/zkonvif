#!/usr/bin/python
# coding=utf-8
# 
# @file: reght.py
# @date: 2014-11-09
# @brief: 实现注册/心跳/注销, 为其他服务提供方便
# @detail:
#
#################################################################

import urllib2, sys, json, io, time, threading, re
from utils import zkutils
from Log import Log


verbose = False
_log = Log('reg/ht')
TIMEOUT = 3 # urllib2.urlopen 的超时 ...

myip = zkutils().myip_real()
mymac = zkutils().mymac()

class GroupOfRegChk:
    ''' 实现一个生成器，每次 next() 就执行一次注册/心跳
        如果服务太多，每隔10秒，连续注册/心跳，会导致网络剧烈抖动，
        因此这里简单的划分为 10 个组，然后每个 1秒执行一组 ....

        当注册成功，则放到心跳组里，当心跳失败，则放到注册组里
    '''
    def __init__(self, myip, obj_desc):
        self.__myip = myip
        self.__10b = [ [], [], [], [], [], [], [], [], [], [] ] # 保存需要注册的
        self.__10bht = [ [], [], [], [], [], [], [], [], [], [] ] # 保存需要心跳的
        self.__distribution(obj_desc)

    def __distribution(self, sds):
        ''' 将服务列表，平均分配到 __10b 中 '''
        i = 0
        for sd in sds:
            if 'url' in sd:
                self.__fixip(sd)

            self.__10b[i].append(sd)
            if verbose:
                print 'INFO: prepare:', sd
            i += 1;
            i %= len(self.__10b)

    def __fixip(self, sd):
        ''' 如果 sd['url'] 中的 ip/host 部分是 <ip> 的话，则修改为本机的 ip '''
        #regex = re.compile('^(([^:/?#]+):)?(//(([^:/?#]+)(:[0-9]+)?))?([^?#]*)(\?([^# ]*))?(#(.*))?')
        #rc = regex.match(sd['url'])
        #if rc and rc.group(5) == '<ip>':
        #    url = sd['url']
        #    sd['url'] = url.replace('<ip>', self.__myip, 1)
        url = sd['url']
        sd['url'] = url.replace('<ip>', self.__myip, 1)

    def reg(self, regop):
        ''' 对下一组，执行注册 
            如果都注册成功了，则不做啥操作 ...
        '''
        i = 0
        while True:
            i %= len(self.__10b)
            self.__reg(regop, self.__10b[i], self.__10bht[i])
            i += 1
            yield

    def __reg(self, op, breg, bht):
        ''' 对 breg 中的进行注册，成功，就从 breg 中删除，并且保持到 bht 中 '''
        for sd in breg:
            if op(sd):
                breg.remove(sd)
                bht.append(sd)

    def ht(self, htop):
        ''' 对下一组执行心跳 '''
        i = 0
        while True:
            i %= len(self.__10bht)
            self.__ht(htop, self.__10b[i], self.__10bht[i])
            i += 1
            yield

    def __ht(self, op, breg, bht):
        ''' 对 bht 中的进行心跳，如果失败，就从 bht 中删除，加到 breg 中 '''
        for sd in bht:
            if not op(sd):
                bht.remove(sd)
                breg.append(sd)

    def unreg(self, unregop, sd_to_unreg):
        ''' 注销 bunreg 中的对象
            简单的从 breg, bht 中查找，找到后，删除，并且执行 unregop
            因为都是单线程操作，安全 ...
        '''
        for b in self.__10b:
            self.__unreg(b, sd_to_unreg, unregop)

        for b in self.__10bht:
            self.__unreg(b, sd_to_unreg, unregop)

    def __unreg(self, b, sd_to_unreg, unregop):
        for sd in b:
            if 'type' in sd and 'id' in sd:
                if sd['type'] == sd_to_unreg['type'] and sd['id'] == sd_to_unreg['id']:
                    if unregop(sd):
                        b.remove(sd)


class RegHtOper:
    ''' 封装到名字服务的操作 '''
    def __init__(self, mgrt_base_url, ip, mac):
        if mgrt_base_url is None:
            mgrt_base_url = self.__load_base_url()
        if verbose:
            print 'INFO: using name service url:', mgrt_base_url
        _log.log('INFO: using nameservice url:' + mgrt_base_url)
        self.__mgrt_base_url = mgrt_base_url
        self.__ip = ip
        self.__mac = mac

    def __get_utf8_body(self, req):
        # FIXME: 更合理的应该是解析 Content-Type ...
        body = '';
        b = req.read().decode('utf-8')
        while b:
            body += b
            b = req.read().decode('utf-8')
        return body

    def reghostop(self, hd):
        ''' hd 为主机描述 '''
        ip = self.__ip
        if 'ip' in hd:
            ip = hd['ip']

        url = self.__mgrt_base_url + 'regHost?mac=%s&ip=%s&hosttype=%s' % \
              (hd['mac'], ip, hd['type'])
        print url

        try:
            req = urllib2.urlopen(url, None, TIMEOUT)
            body = self.__get_utf8_body(req)
            print body
            if body == '':
                return False
            if 'ok' in body:
                return True
            else:
                return False
        except Exception as e:
            print e
            return False

    def reghost_chkop(self, hd):
        ''' FIXME: 其他的需求 ...
        '''
        url = self.__mgrt_base_url + 'listByMac?mac=%s' % (hd['mac'])
        print url
        try:
            req = urllib2.urlopen(url, None, TIMEOUT)
            body = self.__get_utf8_body(req)
            if body == '':
                print '====================== listByMac return null'
                return False
            else:
                return True
        except Exception as e:
            print e
            return False

    def regop(self, sd):
        ''' 服务注册，sd 为服务描述，返回 True 成功 '''
        mac = self.__mac
        if 'mac' in sd:
            mac = sd['mac']

        url = self.__mgrt_base_url + 'registering?serviceinfo=%s_%s_%s_%s_%s' % \
              (self.__ip, mac, sd['type'], sd['id'], sd['url'])
        try:
            req = urllib2.urlopen(url, None, TIMEOUT)
            body = self.__get_utf8_body(req)
            ret = json.loads(body)
        except Exception as e:
            return False

        if u'已经注册' not in ret['info']:
            return False
        return True

    def htop(self, sd):
        ''' 服务心跳，sd 为服务描述，返回 True 成功 '''
        mac = self.__mac
        if 'mac' in sd:
            mac = sd['mac']

        url = self.__mgrt_base_url + 'heartbeat?serviceinfo=%s_%s_%s_%s' % \
              (self.__ip, mac, sd['type'], sd['id'])
        try:
            req = urllib2.urlopen(url, None, TIMEOUT)
            body = self.__get_utf8_body(req)
            ret = json.loads(body)
        except Exception as e:
            return False


        if u'失败' in ret['info']:
            return False
        else:
            return True

    def unregop(self, sd):
        ''' FIXME：因为名字服务端，似乎没有实现这个 ...，总是返回成功吧 '''
        url = self.__mgrt_base_url + 'unRegistering?...'
        return True


    def __load_base_url(self):
    	ret = json.load(io.open(r'../host/config.json', 'r', encoding='utf-8'))
        r = ret['regHbService']
        if ' ' in r['sip'] or ' ' in r['sport']:
            raise Exception("include ' '")
        if r['sip'] == '' or r['sport'] == '':
            raise Exception("include''")

        return 'http://%s:%s/deviceService/'%(r['sip'],r['sport'])


class RegHost(threading.Thread):
    ''' 主机注册 ...
        每个 hd 为：
            { 'mac': host_mac, 'type': host_type, 'ip': host_ip }
        其中 ip 为可选
    '''
    def __init__(self, hds, mgrt_baseurl = None):
        self.__quit = False
        self.__quit_notify = threading.Event()
        self.__mgrt_base_url = mgrt_baseurl
        self.__hds = hds
        threading.Thread.__init__(self)
        self.daemon = True
        self.start()

    def join(self):
        self.__quit = True
        self.__quit_notify.set()
        threading.Thread.join(self)

    def run(self):
        ip = myip
        mac = mymac
        print 'ip:%s, mac:%s' % (ip, mac)

        oper = RegHtOper(self.__mgrt_base_url, ip, mac)
        gos = GroupOfRegChk(ip, self.__hds)

        regfunc = gos.reg(oper.reghostop)
        htfunc = gos.ht(oper.reghost_chkop)

        while not self.__quit:
            if self.__quit_notify.wait(1.0):
                continue
            next(regfunc)
            next(htfunc)
 

class RegHt(threading.Thread):
    ''' 注册一组服务，sds 为列表，每个 sd 为：
            { 'type': service_type, 'id': service_id, 'url': service_url, 'mac': 'xxxxx' }
            注意，其中 url 的 ip 部分，如果使用 <ip> 则将会转换为本机 ip，否则不做任何转换！！
            其中 mac 为可选项，如果不提供，就使用本机的 mac
    '''
    def __init__(self, sds, mgrt_baseurl = None):
        self.__quit = False
        self.__quit_notify = threading.Event()
        self.__mgrt_base_url = mgrt_baseurl
        self.__sds = sds
        self.__lock = threading.RLock()
        self.__unregs = [] # 保存需要主动注销的 ...
        threading.Thread.__init__(self)
        self.daemon = True # 因为有心跳，不调用 unreg()，也是安全的
        self.start()

    def join(self):
        self.__quit = True
        self.__quit_notify.set()
        threading.Thread.join(self)

    def run(self):
        ip = myip
        mac = mymac
        print 'ip:%s, mac:%s' % (ip, mac)

        oper = RegHtOper(self.__mgrt_base_url, ip, mac)
        gos = GroupOfRegChk(ip, self.__sds)

        regfunc = gos.reg(oper.regop)
        htfunc = gos.ht(oper.htop)

        _log.log('working thread started: there are %d services, ip=%s, mac=%s' % (len(self.__sds), ip, mac));

        while not self.__quit:
            if self.__quit_notify.wait(1.0):
                continue
            next(regfunc)
            next(htfunc)
            self.__to_unreg(gos, oper.unregop)
    
    def __to_unreg(self, gos, func):
        self.__lock.acquire()
        for sd in self.__unregs:
            gos.unreg(func, sd)
        self.__lock.release()

    def unreg(self, sd):
        ''' 主动注销 sd 对应的 ... '''
        self.__lock.acquire()
        self.__unregs.append(sd)
        self.__lock.release()


    def unregs(self, sds):
        ''' 主动注销一组 '''
        self.__lock.acquire()
        for sd in sds:
            self.__unregs.append(sd)
        self.__lock.release()




def build_test_hosts():
    ''' 模拟 100台主机 '''
    hosts = []
    n = 1
    while n <= 100:
        host = {}
        host['mac'] = '%012X' % (n)
        host['ip'] = '127.0.0.1'
        host['type'] = 'arm'
        hosts.append(host)
        n += 1
    return hosts

def build_test_services(hds):
    ''' 模拟生成服务列表，
        每个主机生成一个 recording, 三个 ptz 服务
    '''
    ss = []
    for hd in hds:
        s = {}
        s['mac'] = hd['mac']
        s['ip'] = hd['ip']
        s['type'] = 'recording'
        s['url'] = 'http://...'
        s['id'] = '001'
        ss.append(s)

        s['mac'] = hd['mac']
        s['type'] = 'ptz'
        s['url'] = 'http://...'
        s['id'] = 'card01'
        ss.append(s)

        s['mac'] = hd['mac']
        s['type'] = 'ptz'
        s['url'] = 'http://...'
        s['id'] = 'card02'
        ss.append(s)

        s['mac'] = hd['mac']
        s['type'] = 'ptz'
        s['url'] = 'http://...'
        s['id'] = 'card03'
        ss.append(s)
    return ss


if __name__ == '__main__':
    verbose = False

    hds = build_test_hosts()
    sds = build_test_services(hds)

    rh = RegHost(hds)
    rs = RegHt(sds)

    time.sleep(1000000.0)


