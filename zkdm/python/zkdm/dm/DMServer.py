# coding: utf-8

from tornado.web import RequestHandler, Application, url
from tornado.ioloop import IOLoop
import ServicesManager
import sys, os, io, json
import platform
sys.path.append('../')
from common.reght import RegHt
sys.path.append('../host')
from common.utils import zkutils
import Stat
from reg_host import RegHost

_zkutils = zkutils()

_myip = _zkutils.myip_real()
_mac = _zkutils.mymac()


# DM Service 端口
DMS_PORT = 10000
_sm = None # 在 main 中创建

plat = platform.uname()[0]

class HelpHandler(RequestHandler):
    ''' 提示信息 ....
    '''
    def get(self):
        self.render('./help.html')


class ServiceHandler(RequestHandler):
    ''' 处理服务的控制命令 ....
        /dm/<service name>/<operator>?<params ...>
    '''
    def get(self, name, oper):
        rc = {}
        rc['result'] = 'ok'
        rc['info'] = ''

        if oper == 'start':
            if _sm.start_service(name):
                rc['info'] = 'started'
            else:
                rc['result'] = 'err'
                rc['info'] = 'not found or disabled'
        elif oper == 'stop':
            if _sm.stop_service(name):
                rc['info'] = 'stopped'
            else:
                 rc['result'] = 'err'
                 rc['info'] = 'not found or disabled'
        elif oper == 'disable':
            _sm.enable_service(name, False)
            rc['info'] = 'disabled'
        elif oper == 'enable':
            _sm.enable_service(name, True)
            rc['info'] = 'enabled'
        else:
            rc['info'] = 'unknown operator'
        
        self.write(rc)



class ListServiceHandler(RequestHandler):
    ''' 返回服务列表 '''
    def get(self):
        rc = {}
        rc['result'] = 'ok'
        rc['info'] = ''

        ss = _sm.list_services_new()
        value = {}
        value['type'] = 'list'
        value['data'] = ss

        rc['value'] = value

        self.write(rc)

# 全局，用于主动结束 ...
_ioloop = IOLoop.instance()
pm = Stat.PerformanceMonitor()
#pm.start()
rh = RegHt([ {'type':'dm', 'id':'dm', 'url':r'http://<ip>:10000/dm'}])

class InternalHandler(RequestHandler):
    def get(self):
        rc = {}
        rc['result'] = 'ok'
        rc['info'] = ''

        command = self.get_argument('command', 'nothing')
        if command == 'exit':
            rc['info'] = 'exit!!!'
            self.write(rc)
            rh.join()
            global _ioloop
            _ioloop.stop()
        elif command == 'version':
            rc['info'] = 'now, not supported!!!'
            rc['result'] = 'error'
            self.write(rc)

class HostHandler(RequestHandler):
    ''' 返回主机类型 
    '''
    def get(self):
        rc = {}
        rc['result'] = 'ok'
        rc['info'] = ''
        command = self.get_argument('command', 'nothing')
        if command == 'type':
            try:
                f = io.open(r'../host/config.json', 'r', encoding='utf-8')
                s = json.load(f)
                rc['value'] = {}
                rc['value']['type'] = 'dict'
                rc['value']['data'] = {}
                rc['value']['data']['hostType'] = s['host']['type']
                f.close()
            except:
                rc['info'] = 'can\'t get host type'
                rc['result'] = 'err'
        elif command == 'shutdown':
            rc['info'] = 'host is shutdowning ...'
            if plat=='Windows' or plat.find('CYGWIN'):
                os.system(r'c:/Windows/System32/shutdown.exe /s /t 3')
            else:
                os.system(r'sudo /sbin/halt')
        elif command == 'restart':
            print rc
            rc['info'] = 'host is restarting ...'
            if plat == 'Windows' or plat.find('CYGWIN'):
                os.system(r'c:/Windows/System32/shutdown.exe /r /t 3')
            else:
                os.system(r'sudo /sbin/reboot')

        elif command == 'performance':
            stats = pm.get_all()    
            rc['info'] = stats                    
        else:
            rc['info'] = 'can\'t support %s'%(command)
            rc['result'] = 'err'    
        self.write(rc)

def make_app():
    return Application([
            url(r'/dm/help', HelpHandler),
            url(r'/dm/host', HostHandler),
            url(r'/dm/list', ListServiceHandler),
            url(r'/dm/([^/]+)/(.*)', ServiceHandler),
            url(r'/dm/internal', InternalHandler),
            ])

if __name__ == '__main__':
    rgHost =  RegHost(_myip, _mac)
    rgHost.start()
    # 服务管理器，何时 close ??
    _sm = ServicesManager.ServicesManager(_myip, _myip)
    app = make_app()
    app.listen(DMS_PORT)
    _ioloop.start()

    # 此时，必定执行了 internal?command=exit，可以执行销毁 ...
    print 'DM end ....'
    _sm.close()

