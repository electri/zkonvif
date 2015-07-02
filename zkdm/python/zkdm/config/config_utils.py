import os
import json

def read_all_cfgs(cu, cu_session):
	ret = cu.read_cfg()
	ret_session = cu_session.read_cfg()
	ret.update(ret_session)
	return ret

def fn_config(fname, method, parameters = None):
	cu = ConfigUtils(fname)
	cu_session = ConfigUtils(fname + '.session')
	if method == 'get_cfg':
		ret = read_all_cfgs(cu, cu_session)	
		return ret 

	elif method == 'save':
		ret = {'result':'ok', 'info':''}
		if parameters == None:
			ret['result'] = 'error'
			ret['info'] = 'body is empty'
		else:
			kvs  = json.loads(parameters)
			try:
				cu_session.save_cfg(kvs) 
			except Exception as e:
				ret['result'] = 'error'
				ret['info'] = e.message
		return ret

	if method == "get_kvs":
		ret = {}
		kvs = read_all_cfgs(cu, cu_session)
		mask_kvs = {}
		for e in parameters:
			mask_kvs[e] = parameters[e][0]
		mask_kvs.update(kvs)
		
		for e in parameters:
			ret[e] = mask_kvs[e]
		return ret
	
	elif method == 'alter':
		ret = {"result":"ok", "info": ""}
		mask_kvs = {}
		for e in parameters:
			mask_kvs[e] = parameters[e][0]
		kvs = cu.read_cfg()
		kvs.update(mask_kvs)
		try:
			cu_session.save_cfg(kvs)
		except Exception as e:
			ret = {"result":"error", "info":e.message} 
		return ret
		
	else:
		return {'result':'error', 'infor':'%s method dos\'nt exit'%method}

class ConfigUtils:
	def __init__(self, fname):
		self.__fname = fname

	def read_cfg(self):
		data = self.__read_cfg()
		return data

	def __read_cfg(self, suffix =''):
		data = {}

		try:
			if suffix == '':
				fname = self.__fname
			else:
				fname = self.__fname + suffix

			with open(fname, 'r') as fp:
				for line in fp:
					line = line.strip()
					if line != '':
						if line[0] != '#' and  line[0] != ' ':
							words = line.split('=', 1)
							data[words[0]] = words[1]
		except:
			pass
		return	data 

	def save_cfg(self, kvs):
		try:
			s = ''
			for k in kvs:
				s += k + '=' + kvs[k] + '\n'
			s = s.strip()
			with open(self.__fname, 'w') as fp:
					fp.write(s)
		except IOError as e:
			raise Exception(IOError.strerror)

	
if __name__ == "__main__":
	config = ConfigUtils('./copy_card0.config')
	config.alter_cfg({'hva':'50', 'vva':'50'})
