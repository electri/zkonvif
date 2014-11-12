# coding: utf-8


import platform
import threading, time

_platform = platform.uname()[0]


if _platform == 'Windows':
	# 要求必须安装 pywin32 + wmi
	import wmi, pythoncom
else:
	import re, subprocess



class PerformanceMonitor(threading.Thread):
	''' 性能对象，用于查询主机的性能参数，如 cpu, 内存，网络 .... 

			{
				"cpu_rate": 0.05,					# cpu 占用百分比

				"net": [ 						# 返回每块网卡的统计信息
				{ 
					"name": "eth0",
					"recv_rate": 9938.12, 
					"sent_rate": 15333.2 
				},	
				...
				]

				"memory": 
				{ 
					"availabled": 54533321102,		# 可用物理内存
					"committed": 3110029282,		# 已用内存
				}

				"disk": [							# 磁盘返回每个分区的使用情况
				{
					"name": "c:",
					"freedMB": 49383280,
					"totalMB": 89388277,
				}
				{
					"name": "d:",
					...
				}
				...
				]
			}
	'''
	def __init__(self):
		self.__lock = threading.RLock()
		self.__stats = {}
		self.__quit = False	
		if _platform is not 'Windows':
			self.__first_cpu = True
			self.__first_net = True

		threading.Thread.__init__(self)
		self.daemon = True	# 为了无条件结束 ...


	def get_all(self):
		''' 返回所有统计信息 '''
		data = {}
		self.__lock.acquire()
		for key in self.__stats:
			data[key] = self.__stats[key]
		self.__lock.release()
		return data


	def run(self):
		''' 这里收集性能参数，保存 '''
		if _platform == 'Windows':
			pythoncom.CoInitialize()
			c = wmi.WMI()
		else:
			c = None

		while not self.__quit:
			now = time.time()
			cpu_rate = self.__get_cpu_rate(c)
			net_bits = self.__get_nic_bits_in_out(c)
			mem = self.__get_mem_info(c)
			disk = self.__get_disk_info(c)
			self.__lock.acquire()
			self.__stats['cpu_rate'] = cpu_rate
			self.__stats['net'] = net_bits
			self.__stats['memory'] = mem
			self.__stats['disk'] = disk
			self.__lock.release()

			time.sleep(1.0)


	def __get_mem_info(self, c):
		''' 返回内存占用情况

		'''
		if _platform == 'Windows':
			x = c.Win32_PerfFormattedData_PerfOS_Memory()
			ms = [(int(m.AvailableBytes), int(m.CommittedBytes)) for m in x]
			m = ms[0]
			return { 'availabled': m[0], 'committed': m[1] }
		else:
			availabled = 0
			total = 0

			f = open('/proc/meminfo', 'r')
			for line in f:
				r = re.match(r'MemTotal:\s*([0-9]+)\s*kB', line)
				if r is not None:
					total = int(r.group(1))
				
				r = re.match(r'MemFree:\s*([0-9]+)\s*kB', line)
				if r is not None:
					availabled = int(r.group(1))

			f.close()
			return {'availabled': availabled, 'committed': total - availabled }




	def __get_disk_info(self, c):
		''' 返回磁盘占用情况

			
		'''
		if _platform == 'Windows':
			x = c.Win32_PerfFormattedData_PerfDisk_LogicalDisk()
			xr = [( i.name, int(i.FreeMegabytes), int(i.PercentFreeSpace)) for i in x]
			rc = []
			for m in xr:
				i = { "name": m[0], "freedMB": m[1], "totalMB": m[1] * 100 / m[2] }
				rc.append(i)
			return rc
		else:
			df = subprocess.Popen(["df", "-lm"], stdout=subprocess.PIPE)
			output = df.communicate()[0]
			lines = output.split("\n")	# 扔掉第一行

			rc = []

			for line in lines[1:]:
				ss = line.split()
				if len(ss) == 6:
					i = { "name": ss[5], "freedMB": int(ss[3]), "totalMB": int(ss[1]) }
					rc.append(i)
			return rc



	def __get_cpu_rate(self, c):
		if _platform == 'Windows':
			cs = [cpu.LoadPercentage for cpu in c.Win32_Processor()]
			for i, item in enumerate(cs):
				if item is None:
					cs[i] = 0
			
			cpu = int(sum(cs)/len(cs))
			return cpu / 100.0
		else:
			cpu_now = self.__linux_get_cpu_idle()

			if self.__first_cpu:
				self.__first_cpu = False
				delta = 0.0
			else:
				d1 = cpu_now[0] - self.__cpu_last[0]
				d2 = (cpu_now[0]+cpu_now[1]) - (self.__cpu_last[0]+self.__cpu_last[1])
				delta = 1.0 * d1 / d2

			self.__cpu_last = cpu_now

			return delta



	def __linux_get_cpu_idle(self):
		''' 读 /proc/stat 第一行

			cpu  67891300 39035 6949171 2849641614 118251644 365498 2341854 0
				  user    nice  system    idle       iowait    irq   softirq  ??

			这里简单的返回  ( user+nice+system+iowait, idle)
			
		'''
		f = open('/proc/stat', 'r')
		line = f.readline()
		f.close()
		ss = line.split()
		return (int(ss[1]) + int(ss[2]) + int(ss[3]) + int(ss[5]), int(ss[4]))


	def __linux_get_net_stats(self):
		''' 读取 /proc/net/dev，出了 lo, 返回其他的 ..'''
		rc = [] # [('eth0:', xxxxx, xxxxx), ('ppp0:', xxx, xxx)]
		f = open('/proc/net/dev', 'r')
		for line in f:
			ss = line.split()
			if len(ss) == 17 and ss[0].find(':') > 0:
				rc.append((ss[0], int(ss[1]), int(ss[9])))
		f.close()
		return rc


	def __get_nic_bits_in_out(self, c):
		if _platform == 'Windows':
			x = c.Win32_PerfFormattedData_Tcpip_NetworkInterface()
			d = [(n.Name, int(n.BytesReceivedPerSec), int(n.BytesSentPerSec)) for n in x]
			result = []
			for x in d:
				nic = { 'name':x[0], 'recv_rate':x[1], 'sent_rate':x[2] }
				result.append(nic)

			return result
		else:
			curr = self.__linux_get_net_stats()
			now = time.time()

			result = []
			
			if self.__first_net:
				self.__first_net = False
			else:
				for i in range(0, 2):
					if curr[i][0] == 'lo:':
						continue
					delta = (curr[i][0], curr[i][1]-self.__net_last[i][1], curr[i][2]-self.__net_last[i][2])
					result.append({'name':delta[0], 'recved':delta[1], 'sent':delta[2]})

			self.__net_last = curr
			self.__net_stamp = now

			return result



'''
if __name__ == '__main__':
	pm = PerformanceMonitor()
	pm.start()

	while True:
		stats = pm.get_all()
		print stats
		time.sleep(2.0)
'''
