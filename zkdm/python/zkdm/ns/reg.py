#!/usr/bin/python
# coding: utf-8
#
# @file: reg.py
# @date: 2015-01-09
# @brief: 根据当前信息，注册/心跳到平台，实现 target host/serice register 角色
# @detail:
#
#################################################################


import urllib2, time, threading, Queue, sys
sys.path.append("../")
from common.utils import zkutils

PLATFORM_URL='http://172.16.1.14:8080/deviceService/'
TIMEOUT = 3.0


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
        self.__pinding_hosts.put(host_descr)


    def add_service(self, service_descr):
        ''' 增加或更新一个服务信息

            service_descr: 至少包含 mac, ip, type, id
        '''
        self.__pinding_services.put(service_descr)


    def offline_host(self, mac):
        ''' 停止该 mac 对应的所有服务的心跳 '''
        self.__pinding_hosts_death.put(mac)


    def offline_service(self, service_descr):
        ''' 停止一个服务的心跳
        '''
        self.__pinding_services_death.put(service_descr)


    def run(self):
        ''' 轮询
        '''
        self.__hosts = {} # 已经注册的主机，mac 作为 key
        self.__services = [] # 已经注册的服务

        cnt = 0
        while True:
            self.__once1()
            
            if cnt % 10 == 0:
                self.__once10()

            time.sleep(1.0)
            cnt += 1

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


    def __once10(self):
        ''' 1. 心跳服务
            2. 检查 pinding hosts
            3. 检查 pinding services
        '''
        self.__chk_reg_hosts()
        self.__chk_reg_services()
        self.__ht_services()


    def __once1(self):
        ''' 检查是否需要删除服务 '''
        self.__chk_offline_host()
        self.__chk_unreg_service()


    def __next_pinding(self, q):
        try:
            return q.get_nowait()
        except:
            return None


    def __is_new_host(self, hd):
        if hd['mac'] in self.__hosts:
            h = self.__hosts[hd['mac']]
            return h['hosttype'] != hd['hosttype'] or h['ip'] != hd['ip']
        else:
            return True


    def __chk_reg_hosts(self):
        hd = self.__next_pinding(self.__pinding_hosts)
        while hd:
            if self.__is_new_host(hd):
                self.__reg_host(hd)
                self.__hosts[hd['mac']] = hd
            hd = self.__next_pinding(self.__pinding_hosts)


    def __is_new_service(self, sd):
        for s in self.__services:
            if s['mac'] == sd['mac'] and s['id'] == sd['id'] and s['type'] == sd['type']:
                return False
        return True


    def __chk_reg_services(self):
        sd = self.__next_pinding(self.__pinding_services)
        while sd:
            if self.__is_new_service(sd):
                sd['url'] = self.__build_service_url(sd)
                self.__reg_service(sd)
                self.__services.append(sd)
            sd = self.__next_pinding(self.__pinding_services)


    def __chk_offline_host(self):
        mac = self.__next_pinding(self.__pinding_hosts_death)
        while mac:
            for s in self.__services:
                if s['mac'] == mac:
                    self.__services.remove(s)
            mac = self.__next_pinding(self.__pinding_hosts_death)


    def __del_from_service(self, sd):
        for s in self.__services:
            if s['mac'] == sd['mac'] and s['id'] == sd['id'] and s['type'] == sd['type']:
                self.__services.remove(s)
                break


    def __chk_unreg_service(self):
        sd = self.__next_pinding(self.__pinding_services_death)
        while sd:
            self.__del_from_service(sd)
            sd = self.__next_pinding(self.__pinding_services_death)


    def __ht_services(self):
        for s in self.__services:
            self.__ht_service(s)
                

    def __reg_host(self, hd):
        ''' 主机注册到平台 '''
        url = PLATFORM_URL + 'regHost?mac=%s&ip=%s&hosttype=%s' % (hd['mac'], hd['ip'], hd['hosttype'])
        print 'URL:', url
        try:
            urllib2.urlopen(url, None, TIMEOUT)
        except Exception as e:
            print 'EXCEPT: reg_host:', e

    def __reg_service(self, sd):
        ''' 注册服务到平台 '''
        url = PLATFORM_URL + 'registering?serviceinfo=%s_%s_%s_%s_%s' % \
              (self.__ip, sd['mac'], sd['type'], sd['id'], sd['url'])
        print 'URL:', url
        try:
            urllib2.urlopen(url, None, TIMEOUT)
        except Exception as e:
            print 'EXCEPT: reg_service:', e


    def __ht_service(self, sd):
        ''' 服务心跳到平台 '''
        url = PLATFORM_URL + 'heartbeat?serviceinfo=%s_%s_%s_%s' %\
              (self.__ip, sd['mac'], sd['type'], sd['id'])
        print 'URL:', url
        try:
            urllib2.urlopen(url, None, TIMEOUT)
        except Exception as e:
            print 'EXCEPT: ht:', e


if __name__ == '__main__':
    reg = Reg()
    reg.add_host({ 'mac': 'FFFFFFFFFFFF', 'ip': '111.111.111.111', 'hosttype': 'tester' })
    reg.add_service( { 'mac': 'FFFFFFFFFFFF', 'type': 'st', 'id': '001' } )
    time.sleep(60.0)


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

