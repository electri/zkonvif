# coding: utf-8

from tornado.web import RequestHandler, Application, url
from tornado.ioloop import IOLoop
import sys, os, io, json
import platform
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import ServicesManager
sys.path.append('../')
from common.utils import zkutils
from common.reght import RegHt
from common.reght import RegHost
sys.path.append('../host')
#import Stat
from common.utils import zkutils
from common.uty_token import *
import thread 
import pping

_tokens = load_tokens("../common/tokens.json")

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
        global _sm
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
        global _sm
        ss = _sm.list_services_new()
        value = {}
        value['type'] = 'list'
        value['data'] = ss

        rc['value'] = value

        self.write(rc)

class InternalHandler(RequestHandler):
    def get(self):
        rc = {}
        rc['result'] = 'ok'
        rc['info'] = ''

        command = self.get_argument('command', 'nothing')
        if command == 'exit':
            rc['info'] = 'exit!!!'
            self.write(rc)
            global rh
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
        global plat
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
            global pm
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
    
def main():

    _zkutils = zkutils()
    _myip = _zkutils.myip_real()

    _mac = _zkutils.mymac()
    global rh, _tokens
    
    service_url = r'http://%s:10000/dm/0/dm'%(_myip)
    hds = gather_hds_from_tokens(_tokens)
    hds.append({'mac': _myip, 'ip': _myip, 'type': 'dm', 'url' : service_url, 'id': 'dm'}) 
    RegHost(hds)

    sds = gather_sds_from_tokens(_tokens, "dm")
    sds.append({'type': 'dm', 'id': 'dm', 'url': service_url})
    rh = RegHt(sds)
    thread.start_new_thread(ping,('../common/tokens'))
    # 服务管理器，何时 close ??
    global _sm
    _sm = ServicesManager.ServicesManager(_myip, _myip)
    app = make_app()
    global DMS_PORT
    app.listen(DMS_PORT)
    _ioloop.start()

    # 此时，必定执行了 internal?command=exit，可以执行销毁 ...
    print 'DM end ....'
    _sm.close()

import threading

class DMThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        main()

import win32serviceutil
import win32service
import win32event
class DMService(win32serviceutil.ServiceFramework):
    _svc_name_ = "zonekey.service.dm"
    _svc_display_name_ = "zonekey.service.dm"
    _svc_deps_ = ["EventLog"]

    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None) 
        self.dm_thread_ = DMThread()
        # DM Service 端口
        global DMS_PORT 
        DMS_PORT = 10000
        global _sm
        _sm = None # 在 main 中创建
        global plat
        plat = platform.uname()[0]
        # 全局，用于主动结束 ...
        global _ioloop
        _ioloop = IOLoop.instance()
        #global pm
        #pm = Stat.PerformanceMonitor()
        #pm.start()
            
    def SvcStop(self):
        win32event.SetEvent(self.hWaitStop)


    def SvcDoRun(self):
        import servicemanager
        self.dm_thread_.start()
        # wait for beeing stopped...
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)


if __name__ == '__main__':
    # Note that this code will not be run in the 'frozen' exe-file!!!
    win32serviceutil.HandleCommandLine(DMService)

