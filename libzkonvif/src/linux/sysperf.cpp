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
	: ost::Thread(0, 16384)
{
	dp_ = strdup(dp);
	nic_ = strdup(nic);

	net_sr_ = 0.0, net_rr_ = 0.0;

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
		sleep(1000);
		once();
	}
}

void SysPerf::once()
{
	update_cpu();
	update_mem();
	update_disk();
	update_net();
	fprintf(stderr, "\n");
}

void SysPerf::update_cpu()
{
	FILE *fp = fopen("/proc/stat", "r");
	if (fp) {
		long user, nice, system, idle;
		if (4 == fscanf(fp, "cpu %ld %ld %ld %ld", &user, &nice, &system, &idle)) {
			cpurate_ = (user + system) * 1.0 / (user + nice + system + idle);
			fprintf(stderr, "cpu: %.3f ", cpurate_);
		}

		fclose(fp);
	}
}

void SysPerf::update_mem()
{
	FILE *fp = fopen("/proc/meminfo", "r");
	if (fp) {
		char buf[256];
		while (!feof(fp)) {
			char *p = fgets(buf, sizeof(buf), fp);
			if (!p) continue;

			long val;
			char key[64];
			if (sscanf(p, "%s %ld kB", key, &val) == 2) {
				if (!strcmp("MemTotal:", key))
					mem_tot_ = val * 1000.0;
				else if (!strcmp("MemFree:", key))
					mem_used_ = mem_tot_ - val * 1000.0;
			}
		}

		fprintf(stderr, "mem: %.0fM, %.0fM ", mem_tot_/1000000.0, mem_used_/1000000.0);

		fclose(fp);
	}
}

void SysPerf::update_disk()
{
	// using /bin/df
	
	FILE *fp = popen("LANG=C /bin/df", "r");
	if (fp) {
		char buf[256];

		int64_t used, tot;
		char mnt[64];

		while (!feof(fp)) {
			char *p = fgets(buf, sizeof(buf), fp);
			if (!p) continue;
			sscanf(p, "%*s %lld %lld %*lld %*s %[^\r\n]", &tot, &used, mnt);
			if (!strcmp(mnt, dp_)) {
				disk_tot_ = 1000.0 * tot;
				disk_used_ = 1000.0 * used;

				fprintf(stderr, "disk: %.3fG, %.3fG ", disk_tot_/1000000000.0, disk_used_/1000000000.0);

				break;
			}
		}

		pclose(fp);
	}
}


void SysPerf::update_net()
{
	long r = -1, s = 0;

	FILE *fp = fopen("/proc/net/dev", "r");
	if (fp) {
		while (!feof(fp)) {
			char buf[512];
			char *p = fgets(buf, sizeof(buf), fp);
			if (!p) continue;

			char nic[64];
			int rc = sscanf(p, "%63[^:]: %ld %*ld %*ld %*ld %*ld %*ld %*ld %*ld %ld", nic, &r, &s);
			if (rc == 3) {
				char *pnic = nic;
				while (*pnic == ' ' || *pnic == '\t') pnic++;
				if (!strcmp(pnic, nic_)) {
					break;
				}
			}
		}
		fclose(fp);
	}

	if (r > 0) {
		double curr = now();

		if (last_stamp_ > 0.0) {
			net_rr_ = (r - last_r_) / (curr - last_stamp_);
			net_sr_ = (s - last_s_) / (curr - last_stamp_);
		}

		last_stamp_ = curr;
		last_r_ = r;
		last_s_ = s;

		fprintf(stderr, "net: %.0f, %.0f ", net_sr_, net_rr_);
	}
}


#endif // linux

