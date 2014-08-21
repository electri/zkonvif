from datetime import datetime
import time
import sys

from PtzWrap import PtzWrap

try:
	approot = os.path.dirname(os.path.abspath(__file__))
except NameError:	#	We are the main py2exe script, not a module
	approot = os.path.dirname(os.path.abspath(sys.argv[0]))
# this is useless, I feel
os.chdir(approot)

def timeInterval(start):
		end = datetime.now()
		return end - start


print type(sys.argv[1])
print sys.argv[2]
Ptz = PtzWrap()
Ptz.open(sys.argv[1],int(sys.argv[2]))
time.sleep(5.0)

def test_func(method, params, time_interval):
		global Ptz
		start = datetime.now()
		Ptz.call(method, params)
		print timeInterval(start).microseconds
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

		def eachOther(cmd1, ptr1, cmd2, ptr2):
				if (cmd1 == 'set_position')
					ptr = {}
						
def main():
	global Ptz
	isRun = True
	test_all_func()	
	while (isRun):
		a = input('请输入第一个交互命名,若为exit则退出')
		if a = 'exit':
			break
		a.p = input('参数')
		b = input('请输入第二个交互命令')
		b.p = input('参数')
		Ptz.call(a, a,p)
		Ptz.call(b, b.p)
		time.sleep(5.0)
	Ptz.close()

if __name__ == '__main__':
	main()
				

