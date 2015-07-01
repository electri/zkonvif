import os
import json

def get_kvs(kvs, mask_kvs):
	ret = {}
	no_exists = []

	for m_kv in mask_kvs:
		if kvs.__contains__(m_kv):
			ret[m_kv] = kvs[m_kv]
		else:
		 	no_exists.append(m_kv)
				
	return ret, no_exists

def read_all_cfgs(cu, cu_session):
	ret = cu.read_cfg()
	ret_session = cu_session.read_cfg()
	ret.update(ret_session)
	return ret

def fn_config(fname, method, parameters = None):
	old_cwd = os.getcwd()
	os.chdir(os.path.dirname(__file__))
	cu = ConfigUtils(fname)
	cu_session = ConfigUtils(fname + '.session')
	if method == 'get_cfg':
		ret = read_all_cfgs(cu, cu_session)	
		return ret 

	if method == "get_kvs":
		kvs = read_all_cfgs(cu, cu_session)
		return get_kvs(kvs, parameters)

	elif method == 'alter':
		ret = {}
		if parameters == None:
			ret['result'] = 'error'
			ret['info'] = 'body is empty'
		else:
			kvs = {}
			for e in parameters:
				kvs[e] = parameters[e][0]
			return cu_session.alter_cfg(kvs)

	elif method == 'save':
		ret = {}
		if parameters == None:
			ret['result'] = 'error'
			ret['info'] = 'body is empty'
		else:
			kvs  = json.loads(parameters)
			ret = cu_session.save_cfg(kvs) 
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
			old_cwd = os.getcwd()
			os.chdir(os.path.dirname(os.path.abspath(__file__)))	
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
		finally:
			os.chdir(old_cwd)
		return	data 

	def save_cfg(self, kvs):
		ret = {}
		try:
			old_cwd = os.getcwd()
			os.chdir(os.path.dirname(os.path.abspath(__file__)))
			s = ''
			for k in kvs:
				s += k + '=' + kvs[k] + '\n'
			s = s.strip()
			with open(self.__fname, 'w') as fp:
					fp.write(s)

			ret['result'] = 'ok'
			ret['info'] = ''

		except IOError as e:
			ret['result'] = 'error'
			ret['info'] = e.strerror
		finally:
			os.chdir(old_cwd)
		return ret

	def alter_cfg(self, kvs):
		ret = {}	
		try:
			old_cwd = os.getcwd()
			os.chdir(os.path.dirname(os.path.abspath(__file__)))
			with open(self.__fname, 'r') as fp:
				lines = fp.readlines()
			error_keys = self.__alter_values(lines, kvs)
		except IOError as e:
			ret['result'] = 'error'
			ret['info'] = e.strerror
		finally:
			os.chdir(old_cwd)

		try:
			old_cwd = os.getcwd()
			os.chdir(os.path.dirname(os.path.abspath(__file__)))	
			with open(self.__fname, 'w') as fp:
				fp.writelines(lines)
				if error_keys != []:
					ret['result'] = 'error'
					ret['info'] = 'keys list: %s does\'nt exist'%(str(error_keys))
				else:
					ret['result'] = 'ok'
					ret['info'] = ''
		except Exception as e:
			ret['result'] = 'error'
			ret['info'] = e.message
		finally:
			os.chdir(old_cwd)
		return ret
			
	def __alter_value(self, lines, kv):
		err_key = None
		i = 0
		length = len(lines)
		if length == 0:
			return kv

		for no in range(length):
			if lines[no][0] != '#' and lines[no][0] != ' ':
				words = lines[no].split('=', 1)
				if words[0] == kv.keys()[0]:
					suffix = '\n'
					if lines[no][-1] != '\n':
						suffix = ''
					lines[no] =  words[0] + '=' + kv.values()[0] + suffix
					break
			if no  == length - 1:
				err_key = kv.keys()[0]	
		return err_key

	def __alter_values(self, lines, kvs):
		err_keys = []
		for k in kvs:
			ek = self.__alter_value(lines, {k: kvs[k]})
			if ek != None:
				err_keys.append(ek)
		return err_keys 
	
if __name__ == "__main__":
	config = ConfigUtils('./copy_card0.config')
	config.alter_cfg({'hva':'50', 'vva':'50'})
