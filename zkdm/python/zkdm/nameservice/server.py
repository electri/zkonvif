# coding: utf-8
# @file: server.py
# @date: 2014-12-22
# @brief:
# @detail:
#
#################################################################


from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application, url
from dbhlp import DBHlp
import time, json
import sys
import portalocker
import register
import query

sys.path.append('../')

VERSION = 0.9
VERSION_INFO = 'NS Service ...'


# 只是为了支持 internal?command=exit, 可以优雅的结束 ...
_ioloop = IOLoop.instance()

class InternalHandler(RequestHandler):
    ''' 处理内部命令 '''
    def get(self):
        rc = {}
        rc['result'] = 'ok'
        rc['info'] = ''

        cmd = self.__param('command')
        if cmd is None:
            rc['result'] = 'err'
            rc['info'] = '"command" MUST be suppiled!'
            self.write(rc)
            return

        if cmd == 'version':
            ver = {}
            ver['version'] = VERSION
            ver['descr'] = VERSION_INFO
            data = {}
            data['type'] = 'version'
            data['data'] = ver
            rc['value'] = data
            self.write(rc)

        if cmd == 'exit':
            global _ioloop
            rc['info'] = 'exit!!!'
            rh.join()
            self.write(rc)
            _ioloop.stop()
        

    def __param(self, key):
        if key in self.request.arguments:
            return self.request.arguments[key][0]
        else:
            return None

def simple_params(args):
    ''' 将 RequestHandler.request.arguments 简化为字典类型 '''
    params = {}
    for item in args:
        params[item] = args[item][0]
    return params


class RegisterHandler(RequestHandler):
    def get(self, cmd):
        ''' 支持的格式：
                reghost?name=<host name>&type=<host type>
                regservice?host=<host name>&name=<service name>&type=<service type>&url=<service url>
                heartbeat?host=<host name>&name=<service name>&type=<service type>
        '''
        optabs = [ {'cmd': 'reghost', 'func': register.reghost },
                   {'cmd': 'regservice', 'func': register.regservice },
                   {'cmd': 'heartbeat', 'func': register.heartbeat },
                 ]
        params = simple_params(self.request.arguments)
        result = { 'result': 'err', 'info': 'NOT supported cmd:' + cmd }
        for x in optabs:
            if x['cmd'] == cmd:
                result = x['func'](params)

        self.write(result)



class QueryHandler(RegisterHandler):
    def get(self, cmd):
        ''' 支持的格式：
                getAllServices ...
        '''
        optabs = [ { 'cmd': 'getAllServices', 'func': query.getAllServices },
                 ]
        params = simple_params(self.request.arguments)
        result = { 'result': 'err', 'info': 'NOT supported cmd:' + cmd }
        for x in optabs:
            if x['cmd'] == cmd:
                result = x['func'](params)

        self.write(result)


def make_app():
    return Application([
            url(r'/ns/internal', InternalHandler),
            url(r'/ns/register/(.*)', RegisterHandler),
            url(r'/ns/query/(.*)', QueryHandler),
            ])


def main():
    pid_fname = "ns.pid"
    p = open(pid_fname, 'w')
    try:
        portalocker.lock(p, portalocker.LOCK_EX | portalocker.LOCK_NB)
    except:
        print 'ERR: only one instance can be started!!!'
        return

    app = make_app()
    app.listen(9999)
  
    _ioloop.start()

    # 结束 ..
    print 'NS service end ...'



if __name__ == '__main__':
    main()



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

