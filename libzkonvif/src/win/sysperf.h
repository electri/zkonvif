#ifdef WIN32

/** 通过 WMI 接口访问性能计数器，仅仅支持 vista 以上 windows 版本 */
#pragma once

#include <cc++/thread.h>
#define _WIN32_DCOM
#include <wbemidl.h>
# pragma comment(lib, "wbemuuid.lib")

/** 启动一个工作线程，每隔1秒收集统计信息，保存，供查询 */
class SysPerf : ost::Thread
{
	double cpurate_, mem_tot_, mem_used_;
	double disk_tot_, disk_used_;
	double net_sr_, net_rr_;

	bool quit_;

public:
	SysPerf();
	~SysPerf();

	double cpu() const 
	{
		return cpurate_;
	}
	void memory(double &total, double &used) const
	{
		total = mem_tot_, used = mem_used_;
	}
	void disk(double &total, double &used) const
	{
		total = disk_tot_, used = disk_used_;
	}
	void netinfo(double &sentrate, double &recvrate) const
	{
		sentrate = net_sr_, recvrate = net_rr_;
	}

private:
	void run();
	void once(IWbemServices *s);
	void update_cpu(IWbemServices *s);
	void update_mem(IWbemServices *s);
	void update_disk(IWbemServices *s);
	void update_net(IWbemServices *s);
};

#endif // 
