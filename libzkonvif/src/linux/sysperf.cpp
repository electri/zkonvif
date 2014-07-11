#ifdef linux

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "sysperf.h"

SysPerf::SysPerf(const char *dp, const char *nic)
{
	dp_ = strdup(dp);
	nic_ = strdup(nic);

	quit_ = false;
	start();
}

SysPerf::~SysPerf()
{
	quit_ = true;
	join();

	free(dp_);
	free(nic_);
}

void SysPerf::run()
{
	while (!quit_) {
		once();
		sleep(1000);
	}
}

void SysPerf::once()
{
	update_cpu();
	update_mem();
	update_disk();
	update_net();
}

void SysPerf::update_cpu()
{
	FILE *fp = fopen("/proc/stat", "r");
	if (fp) {
		long user, nice, system, idle;
		if (4 == fscanf(fp, "cpu %ld %ld %ld %ld", &user, &nice, &system, &idle)) {
			cpurate_ = (user + system) * 1.0 / (user + nice + system + idle);
		}

		fclose(fp);
	}
}

void SysPerf::update_mem()
{
	FILE *fp = fopen("/proc/meminfo", "r");
	if (fp) {
		char buf[256];
		char *p = fgets(buf, sizeof(buf), fp);
		long val;
		if (sscanf(p, "MemTotal: %ld kB", &val) == 1)
			mem_tot_ = val * 1000.0;

		p = fgets(buf, sizeof(buf), fp);
		if (sscanf(p, "MemFree: %ld kB", &val) == 1)
			mem_used_ = mem_tot_ - val * 1000.0;


		fclose(fp);
	}
}

void SysPerf::update_disk()
{
	// /proc/diskstat, /proc/partitions
}


void SysPerf::update_net()
{
	// /proc/net/netstat
}


#endif // linux

