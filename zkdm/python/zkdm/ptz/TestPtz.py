from datetime import datetime
import time
import sys

from PtzWrap import PtzWrap

def timeInterval(start):
		end = datetime.now().microsecond
		return end - start


print type(sys.argv[1])
print sys.argv[2]
Ptz = PtzWrap()
Ptz.open(sys.argv[1],int(sys.argv[2]))
time.sleep(5.0)

def test_func(method, params, time_interval):
		global Ptz
		Ptz.call(method, params)
		time.sleep(time_interval)
		Ptz.call('stop', {'speed': [2]})
	
def	test_all_func():
		test_func('left', {'speed': [2]}, 5)	
		test_func('right', {'speed': [2]}, 5)
		test_func('up', {'speed': [2]}, 5)
		test_func('down', {'speed': [2]}, 5)
		test_func('set_zoom', {'z': [2]}, 5)
#	test_func('get_zoom', {'speed': [2]}, 5)
		Ptz.get_zoom()
		test_func('set_pos', {'x':[60], 'y':[80], 'sx':[2], 'sy':[2]}, 5)
		test_func('get_pos', {'speed':[2]}, 5)

def main():
	global Ptz
	test_all_func()
	Ptz.close()

if __name__ == '__main__':
	main()
				

