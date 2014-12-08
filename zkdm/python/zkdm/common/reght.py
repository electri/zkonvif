#!/usr/bin/python
# coding=utf-8
# 
# @file: reght.py
# @date: 2014-11-09
# @brief: 实现注册/心跳/注销, 为其他服务提供方便
# @detail:
#
#################################################################

import urllib2, sys, json, io, time, threading
from utils import zkutils

class RegHt(threading.Thread):
    ''' 注册/注销/心跳类, 本质是一个工作现场, 实现周期心跳 ...
            '''
    def __init__(self, service_type, service_id, service_url, mgrt_baseurl = None):
        ''' 初始化并启动工作线程, 直到调用 join 结束
            mgrt_baseurl 为名字服务的基础 url, 如 http://192.168.1.100:8080/deviceService
        '''
        self._service_type = service_type
        self._service_id = service_id
        self._quit = False
        self._mgrt_baseurl = mgrt_baseurl
        self._quit_notify = threading.Event()
        self._myip = zkutils().myip_real()
        self._mymac = zkutils().mymac()
        self.baseurl = 'http://%s:'%(self._myip)
        self._service_url = self.baseurl + service_url 
        threading.Thread.__init__(self)
        self.daemon = True # 因为有心跳, 不调用 unreg() 也是安全的
        self.start()    # 启动工作线程

    def join(self):
        ''' 主动结束 '''
        self._quit = True
        self._quit_notify.set()
        threading.Thread.join(self)     # 等待工作线程结束


    def run(self):
        ''' step:
                1. 注册,直到成功
                2. 每隔10秒, 心跳
                3. 随时处理退出 ...
        '''
        if not self._mgrt_baseurl:
            try:
                self._mgrt_baseurl = self._load_mgrt_baseurl()
            except Exception as e:
                print "error"
                print "\t" + e.message
                print "\t" + sys._getframe().f_code.co_filename
                print "\t" + str(sys._getframe().f_lineno - 5) + 'line'
                print e.message
                sys.exit(0)
        while not self._reg() and not self._quit:
            self._quit_notify.wait(5.000)
        while self._hb and not self._quit:
            self._quit_notify.wait(10.0)
        self._unreg()


    def _log(self, info):
        print info

    def _load_mgrt_baseurl(self):
        # TODO: 从配置中读取 ..
    	ret = json.load(io.open(r'../host/config.json', 'r', encoding='utf-8'))
        r = ret['regHbService']
        if ' ' in r['sip'] or ' ' in r['sport']:
            raise Exception("include ' '")
        if r['sip'] == '' or r['sport'] == '':
            raise Exception("include''")

        return 'http://%s:%s/deviceService/'%(r['sip'],r['sport'])

    def _get_utf8_body(self, req):
        # FIXME: 更合理的应该是解析 Content-Type ...
        body = '';
        b = req.read().decode('utf-8')
        while b:
            body += b
            b = req.read().decode('utf-8')
        return body

    def _reg(self):
        url = self._load_mgrt_baseurl() + 'registering?serviceinfo=%s_%s_%s_%s_%s' % \
              (self._myip, self._mymac, self._service_type, self._service_id, self._service_url)
#self._log("_reg: using url: " + url)
        req = None
        try:
            req = urllib2.urlopen(url)
#except urllib2.HTTPError:
#            self._log('\tHTTPError: ')
#            return False
#        except urllib2.URLError:
#            self._log('\tURLError: ')
#            return False
        except:
#    self._log('\treg return webpage failure')
            return False
        s = self._get_utf8_body(req)
        # TODO: 这里解析注册返回的 json ...
        ret = {}
        try:
            ret.update(json.loads(s))
        except:
            return False
        
        if u'已经注册' not in ret['info']:
            print ret['info']
            return False

        return True

    def _hb(self):
        # TODO:
        url = self._load_mgrt_baseurl() + 'heartbeat?serviceinfo=%s_%s_%s_%s' % \
              (self._myip, self._mymac, self._service_type, self._service_id)
        f = urllib2.urlopen(url)
        s = self._get_utf8_body(f)
        ret = json.loads(s)
        if u'发送的心跳数据' in ret['info']:
            self._log("_hb: url=" + url)
            return True
        else:
            self._log('_hb:url=' + url + 'faile')
            return False
                 
    def _unreg(self):
        # TODO: url = self._load_mgrt_baseurl() + '?????'
        # fuchun zhang can't support unreging a certainly service 
        self._log("unreg  ...")
'''
if __name__ == '__main__':
    th = RegHt('', 'test-id', 'test://...')
    time.sleep(100)
    th.join()
'''

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

