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
import types


VERSION = 0.902
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

        if cmd == 'dump':
            db = DBHlp()
            db.dump("ns.db")
            self.write(rc)
        

    def __param(self, key):
        if key in self.request.arguments:
            return self.request.arguments[key][0]
        else:
            return None
    

def simple_params(args):
    ''' 将 RequestHandler.request.arguments 简化为字典类型 '''
    params = {}
    for item in args:
        # FIXME: 据说 name 字段应该修改为小写 ...
        if item == 'name':
            params['name'] = args['name'][0].lower()
        else:
            params[item] = args[item][0]
    return params


class RegisterHandler(RequestHandler):
    def get(self, cmd):
        ''' 支持的格式：
                reghost?name=<host name>&type=<host type>
                regservice?host=<host name>&name=<service name>&type=<service type>&url=<service url>
                heartbeat?host=<host name>&name=<service name>&type=<service type>
                unregservice?host=<host name>&name=<service name>&type=<service type>
        '''
        optabs = [ {'cmd': 'help', 'func': self.help },
                   {'cmd': 'reghost', 'func': register.reghost },
                   {'cmd': 'regservice', 'func': register.regservice },
                   {'cmd': 'heartbeat', 'func': register.heartbeat },
                   {'cmd': 'unregservice', 'func': register.unregservice },
                 ]
        params = simple_params(self.request.arguments)
        result = { 'result': 'err', 'info': 'NOT supported cmd:' + cmd }
        for x in optabs:
            if x['cmd'] == cmd:
                result = x['func'](params)

        self.write(result)

    def help(self, params):
        info = ''
        apis = dir(register)
        for named in apis:
            if named == 'reghost' or named == 'regservice' or named == 'heartbeat' or named == 'unregservice':
                info += '==== %s ====\n' % (named)
                x = getattr(register, named)
                info += x.__doc__
                info += '\n\n'
        return info


class QueryHandler(RegisterHandler):
    def get(self, cmd):
        ''' 支持的格式：
                getAllService?[offline=1]
                getServicesByType?type=<service type>[&host=<host name>]
        '''
        # 这个表格，可以通过 query 得到，自动生成更合理
        optabs = [ { 'cmd': 'getAllServices', 'func': query.getAllServices },
                   { 'cmd': 'getServicesByType', 'func': query.getServicesByType },
                   { 'cmd': 'help', 'func': self.help },
                   { 'cmd': 'getHosts', 'func': query.getHosts },
                   { 'cmd': 'getServicesByHost', 'func': query.getServicesByHost },
                 ]
        params = simple_params(self.request.arguments)
        result = { 'result': 'err', 'info': 'NOT supported cmd:' + cmd }
        for x in optabs:
            if x['cmd'] == cmd:
                result = x['func'](params)

        self.write(result)

    def help(self, params):
        ''' 打开 query.py，然后显示每个函数的 help ??
        '''
        info = ''
        apis = dir(query)
        for named in apis:
            if named[0:3] == 'get':
                info += '==== %s ====\n' % (named)
                x = getattr(query, named)
                info += x.__doc__
                info += '\n\n'
        return info


class OldRegisterHandler(RequestHandler):
    ''' registering?serviceinfo=<ip>_<mac>_<type>_<id>_<url>
        heartbeat?serviceinfo=<ip>_<mac>_<type>_<id>
        regHost?mac=<mac>&ip=<ip>&hosttype=<type>

        前面两个的定义不好，强制要求 type, id 中不能有 _ 么？
    '''
    def get(self, cmd):
        optabs = [ { 'cmd': 'regHost', 'func': register.reghost },
                   { 'cmd': 'registering', 'func': register.regservice, },
                   { 'cmd': 'heartbeat', 'func': register.heartbeat, },
                 ]
        params = self.conv_params(self.request.arguments)
        result = { 'result': 'err', 'info': 'NOT supported cmd:' + cmd }
        for x in optabs:
            if x['cmd'] == cmd:
                result = x['func'](params)
        self.write(result)

    def conv_params(self, args):
        params = {}
        for x in args:
            if x == 'serviceinfo':
                ss = args[x][0].split('_')
                if len(ss) == 5:
                    params['ip'] = ss[0]
                    params['host'] = ss[1].lower()
                    params['type'] = ss[2]
                    params['name'] = ss[3].lower()
                    params['url'] = ss[4]
                elif len(ss) == 4:
                    params['ip'] = ss[0]
                    params['host'] = ss[1]
                    params['type'] = ss[2]
                    params['name'] = ss[3]
            elif x == 'mac':
                params['name'] = args[x][0].lower()
            elif x == 'ip':
                params['ip'] = args[x][0]
            elif x == 'hosttype':
                params['type'] = args[x][0]

        return params


def make_app():
    return Application([
            url(r'/ns/internal', InternalHandler),
            url(r'/ns/register/(.*)', RegisterHandler),
            url(r'/ns/query/(.*)', QueryHandler),
            url(r'/deviceService/(.*)', OldRegisterHandler), # 仅仅为了兼容张工设计的接口
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
    print 'INFO: server listen on 9999....'
  
    _ioloop.start()

    # 结束 ..
    print 'NS service end ...'



if __name__ == '__main__':
    main()



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

