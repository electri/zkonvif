# coding: utf-8

import sys, os, io, json

def chk_update():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 首先检查是否有更新包 ..
    reboot = False
    try:
        os.chdir('../autoupdate')
        import autoupdate.au as au
        if au.checkVersion():
            # 一旦有更新，则重新机器
            reboot = True
    except:
        pass
    
    if reboot:
        os.system(r'c:/Windows/System32/shutdown.exe /r /t 3')
        sys.exit()


os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append('../')
sys.path.append('../host')

from tornado.web import RequestHandler, Application, url
from tornado.ioloop import IOLoop
import platform
import ServicesManager
from common.utils import zkutils
from common.reght import RegHt
from common.reght import RegHost
import common.reght
#import Stat
from common.utils import zkutils
from common.uty_token import *
import thread 
from pping import *

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
            url(r'/dm/help', HelpHandler),
            url(r'/dm/([^/]+)/dm/host', ProxiedHostHandler), # 中间为 token id
            url(r'/dm/host', HostHandler),
            url(r'/dm/list', ListServiceHandler),
            url(r'/dm/([^/]+)/(.*)', ServiceHandler),
            url(r'/dm/internal', InternalHandler),
            ])
    
def main():
    # 正常启动 ..
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    chk_update()

    import chk_info
    chk_info.wait()

    _zkutils = zkutils()
    _myip = _zkutils.myip_real()

    _mac = _zkutils.mymac()
    global rh, _tokens
    
    service_url = r'http://%s:10000/dm'%(_myip)
    hds = gather_hds_from_tokens(_tokens)
    hds.append({'mac': _myip, 'ip': _myip, 'type': 'dm', 'url' : service_url, 'id': 'dm'}) 
    RegHost(hds)

    #sds = gather_sds_from_tokens(_tokens, "dm")
    #sds.append({'type': 'dm', 'id': 'dm', 'url': service_url})
    #common.reght.verbose = True
    #rh = RegHt(sds)
    os.system('start c:/Python27/python reg_dm.py')

    # 启动 ping
    thread.start_new_thread(ping_all,('../common/tokens.json',))
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

