# coding: utf-8

# 要求必须安装 pywin32 + wmi
import wmi, pythoncom
import threading, time



class PerformanceMonitor(threading.Thread):
	''' 性能对象，用于查询主机的性能参数，如 cpu, 内存，网络 .... '''
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

		first = True
		net_bits_last = (0, 0)
		last = time.time()
		interval = 1.0

		while not self.__quit:
			now = time.time()
			cpu_rate = self.__get_cpu_rate(c)
			net_bits = self.__get_nic_bits_in_out(c) # (recved bits, sent bits)

			if first:
				first = False
				net_bits_delta = (0, 0)
				interval = 1.0
			else:
				interval = now - last
				net_bits_delta = ((net_bits[0]-net_bits_last[0])/interval, (net_bits[1]-net_bits_last[1])/interval)
			
			last = now
			net_bits_last = net_bits
			
			self.__lock.acquire()
			self.__stats['cpu_rate'] = cpu_rate
			self.__stats['net_bits'] = net_bits_delta
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


	def __get_cpu_rate(self, c):
		cs = [cpu.LoadPercentage for cpu in c.Win32_Processor()]
		for i, item in enumerate(cs):
			if item is None:
				cs[i] = 0
			
		cpu = int(sum(cs)/len(cs))
		return cpu / 100.0


	def __get_nic_bits_in_out(self, c):
		d = ([(int(net_interface.BytesReceivedPerSec), int(net_interface.BytesSentPerSec))
				for net_interface in c.Win32_PerfRawData_Tcpip_NetworkInterface()])
		trs = 0
		tss = 0
		for t in d:
			trs += t[0]
			tss += t[1]
		return (trs * 8, tss * 8)


if __name__ == '__main__':
	pm = PerformanceMonitor()
	pm.start()

	while True:
		stats = pm.get_all()
		print stats
		time.sleep(2.0)

