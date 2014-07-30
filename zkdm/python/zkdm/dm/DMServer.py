# coding: utf-8

import subprocess
import json
from pprint import pprint

def load_config(fname):
	''' 加载配置，使用 json 格式 '''
	f = open(fname)
	data = json.load(f)
	f.close()
	return data


def save_config(fname, data):
	''' 将 dict 序列化保存 '''
	f = open(fname, 'w')
	f.write(unicode(json.dumps(data, ensure_ascii = False)))
	f.close()



if __name__ == '__main__':
	data = load_config('config.json')
	pprint(data)
	data['services'][0]['enable'] = False
	save_config('config.json.session', data)
