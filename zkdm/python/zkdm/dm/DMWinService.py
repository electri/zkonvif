#!/usr/bin/python
# coding: utf-8
#
# @file: DMWinService3.py
# @date: 2015-03-12
# @brief:
# @detail:
#
#################################################################
from DMServer3 import *
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
        
        # 全局，用于主动结束 ...
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





# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

