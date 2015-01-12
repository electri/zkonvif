#!/usr/bin/python
# coding: utf-8
#
# @file: reg.py
# @date: 2015-01-09
# @brief: 根据当前信息，注册/心跳到平台，实现 target host/serice register 角色
# @detail:
#
#################################################################


import urllib2, time, threading, Queue, sys, json
sys.path.append("../")
from common.utils import zkutils

PLATFORM_URL='http://172.16.1.14:8080/deviceService/'
TIMEOUT = 3.0
HT_INTEVAL = 10
verbose = False


class Reg(threading.Thread):
    ''' 维护主机注册，服务注册，服务心跳的状态机

        TODO: 优化到平台的request，将调用平均分配在 10 秒的间隔内
        TODO: 根据平台返回进行结果，判断注册是否成功？
    '''

    def __init__(self):
        threading.Thread.__init__(self)
        self.__pinding_hosts = Queue.Queue() # 等待注册的主机
        self.__pinding_services = Queue.Queue() # 等待注册的服务
        self.__pinding_services_death = Queue.Queue() # 用于停止某个服务的心跳
        self.__pinding_hosts_death = Queue.Queue() # 保存需要停止心跳的主机的 mac
        self.daemon = True
        self.__ip = zkutils().myip()
        self.__mac = zkutils().mymac()
        self.start()


    def add_host(self, host_descr):
        ''' 增加或更新一个主机信息
            如果该主机，已经注册过且信息未修改，则忽略

            host_descr: 至少包含 mac, ip, hosttype 三个字段, 使用 mac 作为key
        '''
        if verbose:
            print 'add_host:', host_descr

        self.__fix_mac_ip_url(host_descr)
        self.__pinding_hosts.put(host_descr)


    def add_service(self, service_descr):
        ''' 增加或更新一个服务信息

            service_descr: 至少包含 mac, ip, type, id
        '''
        if verbose:
            print 'add_service:', service_descr

        self.__fix_mac_ip_url(service_descr)
        self.__pinding_services.put(service_descr)


    def offline_host(self, mac):
        ''' 停止该 mac 对应的所有服务的心跳 '''
        if verbose:
            print 'offline host, mac:', mac
        
        if mac == '<mac>':
            mac = self.__mac
        self.__pinding_hosts_death.put(mac)


    def offline_service(self, service_descr):
        ''' 停止一个服务的心跳
        '''
        if verbose:
            print 'offline_service: ', service_descr

        self.__fix_mac_ip_url(service_descr)
        self.__pinding_services_death.put(service_descr)


    def __fix_mac_ip_url(self, d):
        ''' XXX: 因为仅仅代理其他主机，一般来说，不会出现 <mac>, <ip> 这样的关键字 '''
        self.__fixit(d, 'mac', '<mac>', self.__mac)
        self.__fixit(d, 'ip', '<ip>', self.__ip)
        self.__fixit(d, 'url', '<mac>', self.__mac)
        self.__fixit(d, 'url', '<ip>', self.__ip)


    def __fixit(self, o, k, v1, v2):
        if k in o:
            o[k] = o[k].replace(v1, v2)


    def run(self):
        ''' 轮询
        '''
        self.__hosts_b_reg = [ {}, {}, {}, {}, {}, {}, {}, {}, {}, {} ] # 分成10份，每秒注册一份，加起来正好10秒
        self.__service_b_reg = [ [], [], [], [], [], [], [], [], [], [] ] # 分成10份，每秒注册一份，加起来正好10秒
        self.__service_b_ht = [ [], [], [], [], [], [], [], [], [], [] ] # 分成10份，每秒一份，加起来正好10秒

        cnt = 0
        while True:
            self.__once1(cnt)
            time.sleep(1.0)
            cnt += 1



    def __once1(self, cnt):
        self.__chk_new_hosts() 
        self.__chk_new_services()

        self.__chk_offline_host()
        self.__chk_unreg_service()

        idx = cnt % 10
        self.__reg_hosts(self.__hosts_b_reg[idx])
        self.__reg_services(self.__service_b_reg[idx])
        self.__ht_services(self.__service_b_ht[idx])


    def __get_less_b(self, bs):
        l = 1000000
        b = None
        for bb in bs:
            if len(bb) < l:
                l = len(bb)
                b = bb
        return b


    def __next_pinding(self, q):
        try:
            return q.get_nowait()
        except:
            return None


    def __is_new_host(self, hd):
        for bb in self.__hosts_b_reg:
            if hd['mac'] in bb:
                h = bb[hd['mac']]
                return h['hosttype'] != hd['hosttype'] or h['ip'] != hd['ip']
        return True


    def __is_new_service(self, sd):
        for bb in self.__service_b_reg:
            for s in bb:
                if s['mac'] == sd['mac'] and s['id'] == sd['id'] and s['type'] == sd['type']:
                    return False
        return True


    def __chk_new_hosts(self):
        ''' 从 queue 中取出新的主机，分配到 hosts_b_reg 列表中 '''
        hd = self.__next_pinding(self.__pinding_hosts)
        while hd:
            if self.__is_new_host(hd):
                b = self.__get_less_b(self.__hosts_b_reg)
                mac = hd['mac']
                b[mac] = hd
            hd = self.__next_pinding(self.__pinding_hosts)


    def __chk_new_services(self):
        ''' 从 queue 中取出新的服务，分配到 services_b_reg 中，'''
        sd = self.__next_pinding(self.__pinding_services)
        while sd:
            if self.__is_new_service(sd):
                sd['url'] = self.__build_service_url(sd)
                b = self.__get_less_b(self.__service_b_reg)
                b.append(sd)
            sd = self.__next_pinding(self.__pinding_services)


    def __remove_matched(self, b, op):
        for x in b:
            if op(x):
                b.remove(x)


    def __chk_offline_host(self):
        mac = self.__next_pinding(self.__pinding_hosts_death)
        while mac:
            for b in self.__service_b_ht: # 从心跳列表中删除
                self.__remove_matched(b, lambda x: x['mac'] == mac)

            for b in self.__service_b_reg: # 从注册服务列表中删除
                self.__remove_matched(b, lambda x: x['mac'] == mac)
                
            mac = self.__next_pinding(self.__pinding_hosts_death)


    def __chk_unreg_service(self):
        sd = self.__next_pinding(self.__pinding_services_death)
        while sd:
            for b in self.__service_b_ht: # 从心跳列表中删除
                self.__remove_matched(b, 
                        lambda x: x['mac'] == sd['mac'] and x['id'] == sd['id'] and x['type'] == sd['type'])
            for b in self.__service_b_reg: # 从注册服务列表中删除
                self.__remove_matched(b, 
                        lambda x: x['mac'] == sd['mac'] and x['id'] == sd['id'] and x['type'] == sd['type'])

            sd = self.__next_pinding(self.__pinding_services_death)


    def __reg_hosts(self, b):
        for mac in b.keys():
            h = b[mac]
            if self.__reg_host(h):
                del b[mac]


    def __reg_services(self, b):
        ''' 注册成功，则移到 ht 列表中 '''
        for s in b:
            if self.__reg_service(s):
                b.remove(s)
                self.__get_less_b(self.__service_b_ht).append(s)


    def __ht_services(self, b):
        ''' 心跳失败，则移到 reg service 列表中 '''
        for s in b:
            if not self.__ht_service(s):
                b.remove(s)
                self.__get_less_b(self.__service_b_reg).append(s)


    def __get_service_port(self, t):
        ''' TODO: 查询配置，得到服务启动的端口 '''
        if t == 'ptz':
            return 10003
        if t == 'recording':
            return 10006
        return 8000


    def __build_service_url(self, sd):
        ''' http://myip:port/<stype>/<mac>/<sid>
        '''
        url = "http://%s:%d/%s/%s/%s" %\
               (self.__ip, self.__get_service_port(sd['type']), sd['type'], sd['mac'], sd['id'])
        return url


    def __get_utf8_body(self, req):
        # FIXME: 更合理的应该是解析 Content-Type ...
        body = '';
        b = req.read().decode('utf-8')
        while b:
            body += b
            b = req.read().decode('utf-8')
        return body


    def __reg_host(self, hd):
        ''' 主机注册到平台 '''
        url = PLATFORM_URL + 'regHost?mac=%s&ip=%s&hosttype=%s' % (hd['mac'], hd['ip'], hd['hosttype'])
        if verbose:
            print 'URL:', url
        try:
            req = urllib2.urlopen(url, None, TIMEOUT)
            body = self.__get_utf8_body(req)
            if 'ok' in body: # FIXME: 这个判断需要平台确认
                return True
            else:
                return False

        except Exception as e:
            print 'EXCEPT: reg_host:', e
            return False


    def __reg_service(self, sd):
        ''' 注册服务到平台 '''
        url = PLATFORM_URL + 'registering?serviceinfo=%s_%s_%s_%s_%s' % \
              (self.__ip, sd['mac'], sd['type'], sd['id'], sd['url'])
        if verbose:
            print 'URL:', url
        try:
            req = urllib2.urlopen(url, None, TIMEOUT)
            body = self.__get_utf8_body(req)
            ret = json.loads(body)
            
            if u'已经注册' not in ret['info']: # FIXME: 这个判断需要平台确认
                return False 
            else:
                return True

        except Exception as e:
            print 'EXCEPT: reg_service:', e
            return False


    def __ht_service(self, sd):
        ''' 服务心跳到平台 '''
        url = PLATFORM_URL + 'heartbeat?serviceinfo=%s_%s_%s_%s' %\
              (self.__ip, sd['mac'], sd['type'], sd['id'])
        if verbose:
            print 'URL:', url
        try:
            req = urllib2.urlopen(url, None, TIMEOUT)
            body = self.__get_utf8_body(req)
            ret = json.loads(body)

            if u'失败' in ret['info']: # FIXME: 这个判断需要平台确认
                return False
            else:
                return True
            
        except Exception as e:
            print 'EXCEPT: ht:', e
            return False


if __name__ == '__main__':
    verbose = True
    reg = Reg()
    reg.add_host({ 'mac': 'FFFFFFFFFFFF', 'ip': '111.111.111.111', 'hosttype': 'tester' })
    reg.add_service( { 'mac': 'FFFFFFFFFFFF', 'type': 'st', 'id': '001' } )
    reg.add_service( { 'mac': 'FFFFFFFFFFFF', 'type': 'st', 'id': '002' } )
    reg.add_service( { 'mac': 'FFFFFFFFFFFF', 'type': 'st', 'id': '003' } )
    time.sleep(30.0)
    reg.offline_service( { 'mac': 'FFFFFFFFFFFF', 'type': 'st', 'id': '002' } )
    time.sleep(30)
    reg.offline_host( 'FFFFFFFFFFFF' )
    time.sleep(30)
    reg.add_host({ 'mac': 'FFFFFFFFFFFF', 'ip': '111.111.111.111', 'hosttype': 'tester' })
    time.sleep(15)
    reg.add_service( { 'mac': 'FFFFFFFFFFFF', 'type': 'st', 'id': '001' } )
    reg.add_service( { 'mac': 'FFFFFFFFFFFF', 'type': 'st', 'id': '002' } )
    time.sleep(30)
    reg.add_service( { 'mac': 'FFFFFFFFFFFF', 'type': 'st', 'id': '003' } )
    reg.offline_service( { 'mac': 'FFFFFFFFFFFF', 'type': 'st', 'id': '002' } )
    reg.offline_service( { 'mac': 'FFFFFFFFFFFF', 'type': 'st', 'id': '001' } )
    time.sleep(30)



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

