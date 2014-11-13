import reght
import time
class reghtClient: 
	def __init__(self):	
		self.num = 20
			
	def isZero(self, reference):
		num1 = self.num
		if num1 > reference:
			return False
		else:
			return True

if __name__ == '__main__':
	rc = reghtClient()
	reght1 = reght.RegHt('recording', 'recording', '123', None, rc.isZero, 10)
	time.sleep(10000)
