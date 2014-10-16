import win32serviceutil
import win32service
import win32event

a
alive = "I am liuwenwen live"

def getLogger(filePath):
	import logging
	import os
	import inspect

	logger = logging.getLogger("[PythonService]")

	this_file = inspect.getfile(inspect.currentframe())
	dirpath = os.path.abspath(os.path.dirname(this_file))
	handler = logging.FileHandler(os.path.join(dirpath, filePath))
	formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
	handler.setFormatter(formatter)
		
	logger.addHandler(handler)
	logger.setLevel(logging.INFO)

	return logger

logger0 = getLogger("getLiuwenwen1")
logger0.error("i love dady guangyuanliu")
class PythonService(win32serviceutil.ServiceFramework):
	_svc_name_ =  "PythonService"
	_svc_display_name_ = "Python Service Demo"
	
	_svc_description_ = "Python service deomo"

	def __init__(self, args):
		win32serviceutil.ServiceFramework.__init__(self, args)
		self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
		self.logger = getLogger("service.log")
		self.isAlive = True


	def SvcDoRun(self):
		import time
		self.logger.error("svc do run...")
		while self.isAlive:
			self.logger.error(alive)
			time.sleep(1)

		win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

	def SvcStop(self):
		self.logger.error("svc do stop")
#	self.ReportServiceStatus(win32servie.SERVICE_STOP_PENDING)
		win32event.SetEvent(self.hWaitStop)
		self.isAlive = False

if __name__ == '__main__':
	 win32serviceutil.HandleCommandLine(PythonService)
