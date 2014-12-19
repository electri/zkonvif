#!/usr/bin/python
# coding=utf-8
# 
# @file: reght.py
# @date: 2014-11-09
# @brief: 实现注册/心跳/注销, 为其他服务提供方便
# @detail:
#
#################################################################

import urllib2, sys, json, io, time, threading, logging, re
from utils import zkutils

verbose = True

class GroupOfServices:
    ''' 实现一个生成器，每次 next() 就执行一次注册/心跳
        如果服务太多，每隔10秒，连续注册/心跳，会导致网络剧烈抖动，
        因此这里简单的划分为 10 个组，然后每个 1秒执行一组 ....

        当注册成功，则放到心跳组里，当心跳失败，则放到注册组里
    '''
    def __init__(self, myip, services_desc):
        self.__myip = myip
        self.__10b = [ [], [], [], [], [], [], [], [], [], [] ] # 保存需要注册的
        self.__10bht = [ [], [], [], [], [], [], [], [], [], [] ] # 保存需要心跳的
        self.__distribution(services_desc)

    def __distribution(self, sds):
        ''' 将服务列表，平均分配到 __10b 中 '''
        i = 0
        for sd in sds:
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
                print 'INFO reg success: service=', sd
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
                print 'WARNING HT fault：service=', sd
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

    def regop(self, sd):
        url = self.__mgrt_base_url + 'registering?serviceinfo=%s_%s_%s_%s_%s' % \
              (self.__ip, self.__mac, sd['type'], sd['id'], sd['url'])
        try:
            req = urllib2.urlopen(url)
            body = self.__get_utf8_body(req)
            ret = json.loads(body)
        except:
            print 'ERROR: regop: exception, url=', url
            return False

        if u'已经注册' not in ret['info']:
            return False
        return True

    def htop(self, sd):
        url = self.__mgrt_base_url + 'heartbeat?serviceinfo=%s_%s_%s_%s' % \
              (self.__ip, self.__mac, sd['type'], sd['id'])
        try:
            req = urllib2.urlopen(url)
            body = self.__get_utf8_body(req)
            ret = json.loads(body)
        except:
            print 'ERROR: htop: exception, url=', url
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
        # TODO: 从配置中读取 ..
    	ret = json.load(io.open(r'../host/config.json', 'r', encoding='utf-8'))
        r = ret['regHbService']
        if ' ' in r['sip'] or ' ' in r['sport']:
            raise Exception("include ' '")
        if r['sip'] == '' or r['sport'] == '':
            raise Exception("include''")

        return 'http://%s:%s/deviceService/'%(r['sip'],r['sport'])


class RegHt(threading.Thread):
    ''' 注册一组服务，sds 为列表，每个 sd 为：
            { 'type': service_type, 'id': service_id, 'url': service_url }
            注意，其中 url 的 ip 部分，如果使用 <ip> 则将会转换为本机 ip，否则不做任何转换！！
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
        ip = zkutils().myip_real()
        mac = zkutils().mymac()

        oper = RegHtOper(self.__mgrt_base_url, ip, mac)
        gos = GroupOfServices(ip, self.__sds)

        regfunc = gos.reg(oper.regop)
        htfunc = gos.ht(oper.htop)

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



sds = [ { 'type':'test', 'id':'1', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'2', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'3', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'4', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'5', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'6', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'7', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'8', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'9', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'10', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'11', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'12', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'13', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'14', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'15', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'16', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'17', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'18', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'19', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'20', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'21', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'22', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'23', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'24', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'25', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'26', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'27', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'28', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'29', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'30', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'31', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'32', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'33', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'34', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'35', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'36', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'37', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'38', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'39', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'40', 'url':'test://<ip>:11111' },
      ]

sds_minus = [ { 'type':'test', 'id':'1', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'2', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'3', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'4', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'5', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'6', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'7', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'8', 'url':'test://<ip>:11111' },
        { 'type':'test', 'id':'9', 'url':'test://<ip>:11111' },
      ]


if __name__ == '__main__':
    verbose = True
    rh = RegHt(sds)
    time.sleep(600.0);
    rh.unregs(sds_minus)
    time.sleep(60000.0);
    rh.join()

