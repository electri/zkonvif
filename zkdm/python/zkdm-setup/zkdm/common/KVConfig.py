#coding: utf-8
#


class KVConfig(object):
	''' 实现简单的 key=value 存储/查询..
		当保存时，总是创建 .session 新的文件
	'''
	def __init__(self, filename):
		self.__filename = filename
		self.reload()


	def get(self, key, default = None):
		if key in self.__kvs:
			return self.__kvs[key]
		else:
			return default


	def set(self, key, value):
		self.__kvs[key] = value


	def remove(self, key):
		if key in self.__kvs:
			del self.__kvs[key]


	def reload(self):
		self.__kvs = {}
		self.__load_from_file()


	def save(self):
		self.__save_to_file0(self.__kvs, self.__filename + '.session')


	def __load_from_file0(self, name):
		dic = {}
		try:
			f = open(name, 'r')
			for line in f:
				line = line.strip()

				if len(line) == 0:
					continue

				if line[0] == '#':
					continue

				kv = line.split('=', 2)
				if (len(kv) == 2):
					dic[kv[0].strip()] = kv[1].strip()

			f.close()

		except:
		   	pass

		return dic


	def __load_from_file(self):
		self.__kvs = self.__load_from_file0(self.__filename);
		dic = self.__load_from_file0(self.__filename + '.session')
		self.__kvs.update(dic) # 合并 ..


	def __save_to_file0(self, dic, name):
		try:
			f = open(name, 'w')
			for k,v in dic.items():
				f.write(k + '=' + v + '\n')
			f.close()
		except:
			pass




if __name__ == '__main__':
	cfg = KVConfig('test.config')
	name = cfg.get('name')
	if name is None:
		print 'None'
		name = 'sunkw'
		cfg.set('name', name)
		cfg.save()
		exit()

	print name
	print cfg.get('sex')
