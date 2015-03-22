#!/usr/bin/python
# coding: utf-8
#
# @file: td.py
# @date: 2015-03-11
# @brief:
# @detail:
#
#################################################################
import sys, os, io, json

sys.path.append('../')
# 正常启动 ..
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from tornado.web import RequestHandler, Application, url
from tornado.ioloop import IOLoop
from common.utils import zkutils
from common.reght import RegHt
from common.reght import RegHost
import common.reght
sys.path.append('../host')
from common.utils import zkutils
from common.uty_token import *
import thread 
from pping import *

_tokens = load_tokens("../common/tokens.json")
_ioloop = IOLoop.instance()


class ProxiedHostHandler(RequestHandler):
    def get(self, tid):
        print 'recv tid:', tid

        rc = {'result':'ok', 'info':''}
        if tid not in _tokens:
            rc = {'result': 'err', 'info': 'tid of %s NOT found' % tid }
            self.write(rc)
        else:
            # 直接使用 ip, 
            target_ip = _tokens[tid]['ip']
            target_port = 1230
            command = self.get_argument('command', 'nothing')
            if command == 'restart':
                rc = self.__call_arm((target_ip, target_port), 'RecordCmd=Reboot')
            else:
                rc['result'] = 'err'
                rc['info'] = 'NOT impl'
            self.write(rc)

    def __recv_t(self, sock, n, timeout = 2.0):
        import select
        r,w,e = select.select([sock], [], [], timeout)
        if r:
            return sock.recv(n)
        else:
            raise Exception('RECV TIMEOUT')

    def __call_arm(self, addr, cmd):
        print 'call arm: (%s:%d) cmd="%s"' % (addr[0], addr[1], cmd)

        rc={}
        rc['result']='ok'
        rc['info']=''

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            s.settimeout(2)
            s.connect(addr)
            s.settimeout(None)
            s.send(command+"\n")
            # skip UTF-8 BOM
            #s.recv(3)
            self.__recv_t(s, 3, 1.0)
            #message=s.recv(512)
            message = self.__recv_t(s, 512, 1.0)
            message = message.strip()
            rc['info']=message
        except Exception as err:
            rc['result']='error'
            rc['info']=str(err)

        s.close()
        return rc


def make_app():
    return Application([
            url(r'/dm/([^/]+)/dm/host', ProxiedHostHandler), # 中间为 token id
            ])
 

if __name__ == '__main__':
    app = make_app()
    app.listen(10000)
    _ioloop.start()




# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

