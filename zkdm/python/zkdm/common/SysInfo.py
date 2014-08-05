#coding: utf-8

import subprocess
import threading, re, os, time, platform
from utils import zkutils

_alldata = None
_lock = threading.Lock()
_platform = platform.uname()[0]


class __PeriodPerformanceCount(threading.Thread):
	''' 周期获取系统性能计数 '''
	def __init__(self):
		threading.Thread.__init__(self)
		self.daemon = True # 为了直接退出 ...
		self.__current = {}
		self.__lock = threading.Lock()


	def run(self):
		while True:
			time.sleep(1.0)
			self.__obtain()


	def stats(self):
		self.__lock.acquire()
		data = self.__current
		self.__lock.release()
		return data


	def __obtain(self):
		data = {}
		data['cpu'] = self.__get_cpuinfo()
		data['mem'] = self.__get_meminfo()
		self.__lock.acquire()
		self.__current = data
		self.__lock.release()
	

	def __get_cpuinfo(self):
		''' 获取 cpu ... '''
		return 0.0


	def __get_meminfo(self):
		''' 返回内存 ...'''
		return 0.0


_ppc = __PeriodPerformanceCount()
_ppc.start()

		
class SysInfo:
	''' 返回系统信息 '''
	def __init__(self):
		global _alldata
		global _lock

		_lock.acquire()
		if _alldata is None:
			_alldata = self.__loadall()
		self.__all = _alldata
		_lock.release()


	def data(self):
		return self.__all


	def perf_count(self):
		global _ppc
		return _ppc.stats()


	def __loadall(self):
		data = {}
		global _platform
		data['nics'] = self.__get_all_nics()
		return data


	def __get_all_nics(self):
		''' 获取所有网卡参数信息, 来自 ifconfig '''
		nics = []

		p = subprocess.Popen('ifconfig', stdout = subprocess.PIPE, shell = True)
		ss = p.communicate()[0]

		lines = ss.split('\n')

		ifname = re.compile(r'^(eth[\d:]*|wlan[\d:]*|en[0-9:]*)')
		ipaddr = re.compile(r'(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[0-9]{1,2})(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[0-9]{1,2})){3}')
		macaddr = re.compile(r'[A-F0-9a-f:]{17}')

		nic = {}
		for line in lines:
			if ifname.match(line):
				if 'name' in nic and 'mac' in nic and 'ip' in nic:
					nics.append(nic)

				# 说明开始解析新的 nic
				nic = {}
				nic['name'] = ifname.match(line).group()

			if 'name' in nic:
				if macaddr.search(line):
					nic['mac'] = macaddr.search(line).group()

				if ipaddr.search(line):
					nic['ip'] = ipaddr.search(line).group()

		if 'name' in nic and 'mac' in nic and 'ip' in nic:
			nics.append(nic)

		return nics



if __name__ == '__main__':
	si = SysInfo()
	data = si.data()
	print data
