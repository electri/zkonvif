#ifdef linux

#pragma once

#include <cc++/thread.h>

/** 启动一个工作线程，每隔1秒收集统计信息，保存，供查询 */
class SysPerf : ost::Thread
{
	double cpurate_, mem_tot_, mem_used_;
	double disk_tot_, disk_used_;
	double net_sr_, net_rr_;

	bool quit_;

	char *dp_, *nic_;

public:
	SysPerf(const char *dp, const char *nic_name);	// 指定磁盘分区名字，如 "c:"，指定网卡名字 ...
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
	void once();
	void update_cpu();
	void update_mem();
	void update_disk();
	void update_net();

	long last_r_, last_s_;
	double last_stamp_;
};

#endif // 
