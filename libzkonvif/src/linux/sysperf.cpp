#ifdef linux

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "sysperf.h"
#include <sys/time.h>

static double now()
{
	struct timeval tv;
	gettimeofday(&tv, 0);
	return tv.tv_sec + tv.tv_usec / 1000000.0;
}

SysPerf::SysPerf(const char *dp, const char *nic)
{
	dp_ = strdup(dp);
	nic_ = strdup(nic);

	last_stamp_ = -1.0;

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
	// using /bin/df
	
	FILE *fp = popen("/bin/df", "r");
	if (fp) {
		char buf[256];

		int64_t used, tot;
		char mnt[64];

		while (!feof(fp)) {
			char *p = fgets(buf, sizeof(buf), fp);
			if (!p) continue;
			sscanf(p, "%*s %lld %lld %*lld %s %[^\r\n]", &tot, &used, mnt);
			if (!strcmp(mnt, dp_)) {
				disk_tot_ = 1000.0 * tot;
				disk_used_ = 1000.0 * used;
				break;
			}
		}

		pclose(fp);
	}
}


void SysPerf::update_net()
{
	// /proc/net/dev，每个一段时间读取，减得差除以时间，即可计算速度
	long r = -1, s;

	FILE *fp = fopen("/proc/net/dev", "r");
	if (fp) {
		while (!feof(fp)) {
			char buf[1024];
			char *p = fgets(buf, sizeof(buf), fp);
			if (!p) continue;

			char nic[64];
			if (sscanf(p, "%[^:]: %ld %*d %*d %*d %*d %*d %*d %*d %ld", nic, &r, &s) == 10) {
				if (!strcmp(nic, nic_))
					break;
			}
		}
		fclose(fp);
	}

	if (r > 0) {
		double curr = now();
		if (last_stamp_ > 0) {
			net_rr_ = (r - last_r_) / (curr - last_stamp_);
			net_sr_ = (s - last_s_) / (curr - last_stamp_);
		}

		last_stamp_ = curr;
		last_r_ = r;
		last_s_ = s;
	}
}


#endif // linux

