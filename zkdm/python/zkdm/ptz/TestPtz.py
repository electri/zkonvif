import re, sys
from datetime import datetime
import time
sys.path.append('../')

from common.KVConfig import KVConfig
from PtzWrap import Ptz

def timeInterval(start):
		end = datetime.now().microsecond
		return end - start

def load_ptz_config(cfg, who):
		'''this imitate colleague sun'''
		config = {}
		fname = cfg.get(who)
		if fname:
			c = KVConfig(fname)
			config['serial_name'] = c.get('serial_name', 'COMX')
			config['addr'] = c.get('addr', '1')
			config['ptz'] = Ptz()
			if config['ptz'].open(config['serial_name'], int(config['addr'])):
				pass
			else
			 	print('ptz open failed, so exit')
			 	exit()
		return config

_cfg = KVConfig('ptz.config')
_config = load_ptz_config(_cfg, 'test')

def test_func(method,params, time_interval):
		global _config
		_config['ptz'].call(method, params)
		time.sleep(time_interval)
# FIXME: is this syntax mistaken?
		_config['ptz'].call('stop')
	
def	test_all_func():
		test_func('left', 2,  0.2)	
		test_func('right', 2, 0.2)
		test_func('up', 2, 0.2)
		test_func('down', 2, 0.2)
		test_func('set_zoom', 2, 0.2)
		test_func('get_zoom')
		test_func('set_pos', {'x':60, 'y':80, 'sx':2, 'sy':2}
		test_func('get_pos')

def main():
	test_all_func()
	pass

if __name__ = '__main__':
	main()
				

 
