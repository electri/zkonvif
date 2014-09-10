# coding: utf-8

# 要求必须安装 pywin32 + wmi
import wmi, pythoncom
import threading, time



class PerformanceMonitor(threading.Thread):
	''' 性能对象，用于查询主机的性能参数，如 cpu, 内存，网络 .... 

			{
				"cpu_rate": 0.05,					# cpu 占用百分比

				"net_bits": 						# 每秒接收，发送 bits 数
				{ 
					"recv": 9938.12, 
					"sent" 15333.2 
				},	

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

		threading.Thread.__init__(self)
		self.daemon = True	# 为了无条件结束 ...


	def run(self):
		''' 这里收集性能参数，保存 '''
		pythoncom.CoInitialize()
		c = wmi.WMI()

		while not self.__quit:
			now = time.time()
			cpu_rate = self.__get_cpu_rate(c)
			net_bits = self.__get_nic_bits_in_out(c)
			mem = self.__get_mem_info(c)
			disk = self.__get_disk_info(c)

			self.__lock.acquire()
			self.__stats['cpu_rate'] = cpu_rate
			self.__stats['net_bits'] = net_bits
			self.__stats['memory'] = mem
			self.__stats['disk'] = disk
			self.__lock.release()

			time.sleep(1.0)


	def get_all(self):
		''' 返回所有统计信息 '''
		data = {}
		self.__lock.acquire()
		for key in self.__stats:
			data[key] = self.__stats[key]
		self.__lock.release()
		return data


	def __get_mem_info(self, c):
		''' 返回内存占用情况

		'''
		x = c.Win32_PerfFormattedData_PerfOS_Memory()
		ms = [(int(m.AvailableBytes), int(m.CommittedBytes)) for m in x]
		m = ms[0]
		return { 'availabled': m[0], 'committed': m[1] }


	def __get_disk_info(self, c):
		''' 返回磁盘占用情况

			
		'''
		x = c.Win32_PerfFormattedData_PerfDisk_LogicalDisk()
		xr = [( i.name, int(i.FreeMegabytes), int(i.PercentFreeSpace)) for i in x]
		rc = []
		for m in xr:
			i = { "name": m[0], "freedMB": m[1], "totalMB": m[1] * 100 / m[2] }
			rc.append(i)
		return rc


	def __get_disk_storage(self, c):
		''' 返回磁盘总空间，剩余空间 ...
		'''
		pass


	def __get_cpu_rate(self, c):
		cs = [cpu.LoadPercentage for cpu in c.Win32_Processor()]
		for i, item in enumerate(cs):
			if item is None:
				cs[i] = 0
			
		cpu = int(sum(cs)/len(cs))
		return cpu / 100.0


	def __get_nic_bits_in_out(self, c):
		x = c.Win32_PerfFormattedData_Tcpip_NetworkInterface()
		d = ([(int(n.BytesReceivedPerSec), int(n.BytesSentPerSec)) for n in x])
		trs = 0
		tss = 0
		for t in d:
			trs += t[0]
			tss += t[1]
		return { 'recv': trs * 8, 'sent': tss * 8 }



if __name__ == '__main__':
	pm = PerformanceMonitor()
	pm.start()

	while True:
		stats = pm.get_all()
		print stats
		time.sleep(2.0)

