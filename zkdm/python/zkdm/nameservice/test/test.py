#!/usr/bin/python
# coding=utf-8
# 
# @file: test.py
# @date: 2014-12-22
# @brief:
# @detail:
#
#################################################################

import urllib2, time

NSURL = 'http://localhost:9999/ns'

def reghost(name, t):
    ''' 主机注册 '''
    url = NSURL + '/register/reghost?name=%s&type=%s' % (name, t)
    urllib2.urlopen(url)


def regservice(host, name, t, url):
    ''' 服务注册 '''
    url = NSURL + '/register/regservice?host=%s&name=%s&type=%s&url=%s' % (host, name, t, url)
    urllib2.urlopen(url)


def heartbeat(host, name, t):
    ''' 服务心跳 '''
    url = NSURL + '/register/heartbeat?host=%s&name=%s&type=%s' % (host, name, t)
    urllib2.urlopen(url)


def one(name, t):
    ''' 模拟注册一台主机，为其模拟注册10个服务 '''
    ss = []
    reghost(name, t)
    for i in range(0, 10):
        sname = 'test_%d' % i
        url = 'test://172.16.1.103:9998/test/%d' % i
        regservice(name, sname, 'test', url)
        ss.append((name, sname, 'test'))
    return ss


import threading

def async_many(s, e):
    print 'from %d to %d' % (s, e)
    t1 = time.time()
    for i in range(s, e): # 模拟N台，每台10个服务
        hostname = 'abc_%05x' % i
        one(hostname, 'htype')
    t2 = time.time()
    print 'END: from %d to %d, using %f seconds' % (s, e, t2-t1)

if __name__ == '__main__':
    step = 125 
    start, end = 0, step
    for i in range(0, 8):
        th = threading.Thread(target=async_many, args=(start, end))
        th.start()
        start += step
        end = start + step

    while True:
        time.sleep(10)


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

