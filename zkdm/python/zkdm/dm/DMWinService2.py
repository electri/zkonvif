# coding: utf-8

import platform, os, sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append('../')
import win32serviceutil
import win32service
import win32event
import threading
import DMServer2

class DMThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        DMServer2.mainp()


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

