# coding: utf-8

import LocalConfig
import subprocess, shlex
import threading, time
import sys, re
import threading

sys.path.append('../')
from common.utils import zkutils


# 本地配置文件
FNAME = 'config.json'


class ServicesManager:
	''' 本地服务管理
		包括：
		  	启动/停止服务，
			使能/禁用服务
			返回服务列表 ...
		
		FIXME: title 不需要，显示名字放在平台端 ...
		XXX: 是否启动工作线程，轮询服务状态？..
		XXX: 如果服务已经启动了，怎么办？..
	'''
	def __init__(self):
		u = zkutils()
		self.__ip = u.myip()			# 可能是交换机映射后的 ip
		self.__ip_real = u.myip_real()
		self.__activated = [] # (p, sd, url)
		self.__start_all_enabled()
		self.pcs_paras_ = []
		self.services_ = []
		self.mtx_reg_ = threading.Lock()
		self.mtx_hb_ = threading.Lock() 
		regThread = regHb.regClass(self.pcs_paras_, self.services_, self.mtx_reg_, self.mtx_hb_)  
		hbThread = regHb.HbClass(self.services_, self.mtx_hb_)
		regThread.start()
		hbThread.start()

	def list_services(self):
		''' 返回所有服务列表, 并且将服务的 url 中的 ip 部分，换成自己的 ..
		'''
		ssd = LocalConfig.load_config(FNAME)
		ss = ssd['services']
		for s in ss:
			if 'url' in s:
				new_url = self.__fix_url(s['url'])
				s['url'] = new_url
		return ss


	def dump_activated(self):
		''' poll 状态 ...'''
		print '--- dump ---'
		for x in self.__activated:
			print '  ==> ', x[1]['name'], ': state:', x[0].poll()
		print '============'


	def close(self):
		''' 强制关闭所有启动的服务 ???? '''
		while len(self.__activated) > 0:
			print ' ==> to kill "', self.__activated[0][1]['name'], '"'
			self.__stop_service(self.__activated[0][1])


	def start_service(self, name):
		''' 启动服务，如果 name 存在 '''
		ssd = self.list_services()
		for x in ssd:
			if x['name'] == name and x['enable']:
				self.__start_service(x)
				return True
		return False



	def stop_service(self, name):
		''' 停止服务 '''
		ssd = self.list_services()
		for x in ssd:
			if x['name'] == name:
			   self.__stop_service(x)
			   return True
		return False



	def __fix_url(self, url):
		''' 将 url 中的 ip 部分换成本机 ip
			在配置中，url 的格式为：
			  <protocol>://<ip>:<port>/path

			  如 http://<ip>:10001/event
			  需要就 <ip> 替换为本机实际 ip 地址
		'''
		return url.replace(r'<ip>', self.__ip)



	def __start_all_enabled(self):
		''' 启动所有允许的服务 ..
			返回启动的服务的数目 ..
		'''
		n = 0
		for sd in self.list_services():
			if sd['enable']:
				n += 1
				sr = self.__start_service(sd)
				if sr:
					self.__activated.append(sr)
		return n


	def __start_service(self, sd):
		''' 启动服务, 首先检查是否已经启动 ??. 

			总是使用 subprocess.Popen class ..
			TODO:  if !fork 直接启动 py 脚本？是否能在 arm 上节省点内存？ ..
		'''
		for s in self.__activated:
			if s[1]['name'] == sd['name']:
				return None # 已经启动 ..

		args = shlex.split(sd['path'])
		print ' ==> start', args
		p = subprocess.Popen(args)
		print '        pid:', p.pid
		return (p, sd, self.__fix_url(sd['url']))
		

	def __stop_service(self, sd):
		''' 停止服务, 通过发送 internal?command=exit 结束
		'''
		print '--- try stop "' + sd['name'] + '"'
		for s in self.__activated:
			if s[1]['name'] == sd['name']:
				# 首先发出 internal?command=exit 
				url = s[2] + '/internal?command=exit'
				print 'url:', url
				import urllib2, time
				urllib2.urlopen(url)
				
				time.sleep(0.5) # FIXME: 这里等待500ms，然后再强制杀掉 ？？？..

				try:
					s[0].kill()
				except: # 一般情况下， exit command 就能结束 ..
					pass

				print 'service:', s[1]['name'], ' has killed!'

				self.__activated.remove(s)
				break


	def enable_service(self, name, en = True):
		''' 使能/禁用服务 '''
		ssd = LocalConfig.load_config(FNAME)
		for s in ssd['services']:
			if s['name'] == name:
			   s['enable'] = en
			   break
		LocalConfig.save_config(FNAME, ssd)



if __name__ == '__main__':
	sm = ServicesManager()
	all = sm.list_services()
	print all
	count = 10
	while count > 0:
		count -= 1
		time.sleep(1.0)
		sm.dump_activated()
	sm.enable_service('event service', True)
	sm.close()
