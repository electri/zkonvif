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
    print url
    urllib2.urlopen(url)


def regservice(host, name, t, url):
    ''' 服务注册 '''
    url = NSURL + '/register/regservice?host=%s&name=%s&type=%s&url=%s' % (host, name, t, url)
    print url
    urllib2.urlopen(url)


def heartbeat(host, name, t):
    ''' 服务心跳 '''
    url = NSURL + '/register/heartbeat?host=%s&name=%s&type=%s' % (host, name, t)
    print url
    urllib2.urlopen(url)


if __name__ == '__main__':
    host = '123456abcdef'
    host_type = 'x86'
    service_name = 'student'
    service_type = 'ptz'
    service_url = 'http://127.0.0.1:10003/ptz/0/student'

    reghost(host, host_type)
    regservice(host, service_name, service_type, service_url)

    while True:
        time.sleep(10)
        heartbeat(host, service_name, service_type)


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

