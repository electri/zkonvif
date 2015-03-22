import reght
import threading
import time
class reghtClient(threading.Thread): 
	def __init__(self):	
		threading.Thread.__init__(self)
		self.num = 0
		self.mutrix = threading.Lock() 
		self.reght = reght.RegHt('recording', 'recording', '123', None, self.isZero, 10)
		self.start()
	def isZero(self, reference):
		self.mutrix.acquire()
		num1 = self.num
		self.mutrix.release()
		if num1 > reference:
			return False
		else:
			return True

	def run(self):
		while True:
			time.sleep(3)
			self.mutrix.acquire()
			self.num += 1
			self.mutrix.release()	
		
if __name__ == '__main__':
	rc = reghtClient()
	
