#!/usr/bin/python
# coding=utf-8
# 
# @file: reght.py
# @date: 2014-11-09
# @brief: 实现注册/心跳/注销, 为其他服务提供方便
# @detail:
#
#################################################################

import urllib2, sys, json, io, time, threading, logging
from utils import zkutils

class GroupOfServices:
    ''' 实现一个生成器，每次 next() 就执行一次注册/心跳
        如果服务太多，每隔10秒，连续注册/心跳，会导致网络剧烈抖动，
        因此这里简单的划分为 10 个组，然后每个 1秒执行一组 ....
    '''
    def __init__(self, services_desc):
        self.__10b = [ [], [], [], [], [], [], [], [], [], [] ] # 保存需要注册的
        self.__10bht = [ [], [], [], [], [], [], [], [], [], [] ] # 保存需要心跳的
        self.__distribution(services_desc)


    def __distribution(self, sds):
        ''' 将服务列表，平均分配到 __10b 中 '''
        i = 0
        for sd in sds:
            self.__10b[i].append(sd)
            i += 1;
            i %= len(self.__10b)


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
            for sd in self.__10bht[i]:
                htop(sd)
            i += 1
            yield


class RegHtOper:
    def __init__(self, mgrt_base_url, ip, mac):
        if mgrt_base_url is None:
            mgrt_base_url = self.__load_base_url()
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
            print 'regop: exception, url=', url
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
            print 'htop: exception, url=', url
            return False

        if u'发送的心跳数据' in ret['info']:
            return True
        else:
            return False

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
    '''
    def __init__(self, sds, mgrt_baseurl = None):
        self.__quit = False
        self.__quit_notify = threading.Event()
        self.__mgrt_base_url = mgrt_baseurl
        self.__sds = sds
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
        gos = GroupOfServices(self.__sds)

        regfunc = gos.reg(oper.regop)
        htfunc = gos.ht(oper.htop)

        while not self.__quit:
            if self.__quit_notify.wait(1.0):
                continue
            next(regfunc)
            next(htfunc)



sds = [ { 'type':'test', 'id':'1', 'url':'test://172.16.1.103:11111' },
        { 'type':'test', 'id':'2', 'url':'test://172.16.1.103:11111' },
        { 'type':'test', 'id':'3', 'url':'test://172.16.1.103:11111' },
        { 'type':'test', 'id':'4', 'url':'test://172.16.1.103:11111' },
      ]


if __name__ == '__main__':
    rh = RegHt(sds)
    time.sleep(30.0);
    rh.join()

