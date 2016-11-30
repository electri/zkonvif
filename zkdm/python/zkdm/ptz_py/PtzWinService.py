import PtzServer as ps
import threading

class PtzThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        ps.main()

import win32serviceutil
import win32service
import win32event
class PtzService(win32serviceutil.ServiceFramework):
    _svc_name_ = "zonekey.service.Ptz"
    _svc_display_name_ = "zonekey.service.Ptz"
    _svc_deps_ = ["EventLog"]

    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None) 
        self.ptz_thread_ = PtzThread()
        
    def SvcStop(self):
        win32event.SetEvent(self.hWaitStop)


       def SvcDoRun(self):
        import servicemanager
        self.ptz_thread_.start()
        # wait for beeing stopped...
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)


if __name__ == '__main__':
    # Note that this code will not be run in the 'frozen' exe-file!!!
    win32serviceutil.HandleCommandLine(PtzService)

