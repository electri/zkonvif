#include <stdio.h>
#include <stdlib.h>
#include "KVConfig.h"
#include <vector>
#include <map>
#include <string>
#include <math.h>
#include <time.h>
#include <sstream>

#ifdef WIN32
#	define VISCA_WIN
#   include "../../3rd/libvisca-1.1.0/visca/libvisca.h"
#	include <Windows.h>
#else
#	include <visca/libvisca.h>
#endif 
#include "ptz.h"
#include "ZoomValueConvert.h"

#ifdef WIN32
#include <Windows.h>

static double now()
{
	return GetTickCount() / 1000.0;
}
#else
#include <sys/time.h>

static double now()
{
	struct timeval tv;
	gettimeofday(&tv, 0);
	return tv.tv_sec + tv.tv_usec / 1000000.0;
}

#endif

class TimeUsed
{
	std::string info_;
	double d_, b_;

public:
	TimeUsed(const char *info, double d = 0.05)
	{
		info_ = info;
		d_ = d;
		b_ = now();
	}

	~TimeUsed()
	{
		double curr = now();
		if (curr - b_ > d_) {
			fprintf(stderr, "WARNING: Timeout: %s, using %.3f\n", info_.c_str(), curr - b_);
		}
	}
};

namespace {
	struct Serial;
	struct Ptz
	{
		Serial *serial;
		int addr;
		VISCACamera_t cam;
		bool pos_changing, first_get_pos;
		int last_x, last_y;
		int set_posing;	// set_pos() 非常耗时，需要连续 get_pos() 不变后，才认为到位了
		

		ZoomValueConvert *zvc;
		KVConfig *cfg;
	};

	struct Serial
	{
		VISCAInterface_t iface;
		std::vector<Ptz*> cams;
	};

	typedef std::map<std::string, Serial*> SERIALS;
	static SERIALS _serials;
};

ptz_t *ptz_open(const char *name, int addr)
{
	fprintf(stderr, "DEBUG: %s: try to open serial name: %s, addr=%d\n", __FUNCTION__, name, addr);

		//XXX:当 addr = 0时, 程序最后三行会出问题 
	if (!name) return 0;
	if (addr > 7 || addr < 0) return 0;

	SERIALS::const_iterator itf = _serials.find(name);
	if (itf == _serials.end()) {
		Serial *serial = new Serial;
		_snprintf(serial->iface.name, sizeof(serial->iface.name), "%s", name);
		if (VISCA_open_serial(&serial->iface, name) == VISCA_FAILURE) {
			printf("ERR: %s: can't open '%s'\n", __func__, name);
			_serials[name] = serial; // 下次没有必要再试了 ..
			return 0;
		}

#if 0
		int m;
		VISCA_set_address(&serial->iface, &m);
		fprintf(stdout, "DEBUG: %s: %s: m=%d\n", __FUNCTION__, name);
#endif 
		
		printf("name = %s, addr = %d\n", name, addr); 

		serial->iface.broadcast = 0;

		for (int i = 0; i < 8; i++) {
			serial->cams.push_back(0);
		}

		_serials[name] = serial;
		return ptz_open(name, addr);
	}
	else {
		Serial *serial = itf->second;
		if (serial->cams.empty()) {
			// 说明该串口曾经测试过，不可用 ...
			printf("ERR: %s: can't open '%s'\n", __func__, name);
			return 0;
		}

		if (!serial->cams[addr]) {
			Ptz *ptz = new Ptz;
			ptz->cfg = 0;
			ptz->zvc = 0;
			ptz->pos_changing = false;
			ptz->first_get_pos = true;
			ptz->set_posing = 1;
			ptz->serial = serial;
			ptz->addr = addr;
			ptz->cam.address = ptz->addr;

			serial->cams[addr] = ptz;
		}
		else {
			fprintf(stderr, "WARNING: %s: ptz has been opened!!!\n", __FUNCTION__);
		}

		return (ptz_t*)serial->cams[addr];
	}
}

ptz_t *ptz_open_with_config(const char *cfg_name)
{
	fprintf(stderr, "DEBUG: %s: cfg_name=%s\n", __FUNCTION__, cfg_name);

	KVConfig *cfg = new KVConfig(cfg_name);
	
	const char *serial_name = cfg->get_value("ptz_serial_name", "COMX");
	int addr = atoi(cfg->get_value("ptz_addr", "1"));

	ptz_t *p = ptz_open(serial_name, addr);
	if (p) {
		Ptz *ptz = (Ptz*)p;
		ptz->cfg = cfg;
		ptz->zvc = new ZoomValueConvert(ptz->cfg);
		VISCA_set_bugfix(&ptz->serial->iface, (BugFix)atoi(ptz->cfg->get_value("bug_fix", "0")));
	}

	fprintf(stderr, "DEBUG: %s: ret %p\n", __FUNCTION__, p);
	return p;
}

void ptz_close(ptz_t *ptz)
{
	// TODO: 应该根据串口的引用计数关闭 ...
	// FIXME:  ...
	Ptz *p = (Ptz*)ptz;
	VISCA_close_serial(&p->serial->iface);
}


int ptz_stop(ptz_t *ptz)
{
	Ptz *p = (Ptz*)ptz;
	std::stringstream ss;
	ss << __FUNCTION__ << ':' << p->serial->iface.name;
	TimeUsed tu(ss.str().c_str());
	if (VISCA_set_pantilt_stop(&p->serial->iface, &p->cam, 0, 0) != VISCA_SUCCESS)
		return VISCA_FAILURE;
	p->pos_changing = false;
	return VISCA_SUCCESS;
}

int ptz_left(ptz_t *ptz, int speed)
{
	Ptz *p = (Ptz*)ptz;
	if (VISCA_set_pantilt_left(&p->serial->iface, &p->cam, speed, speed) != VISCA_SUCCESS)
		return VISCA_FAILURE;

	p->pos_changing = true;
	return VISCA_SUCCESS;
}

int ptz_right(ptz_t *ptz, int speed)
{
	Ptz *p = (Ptz*)ptz;
	if (VISCA_set_pantilt_right(&p->serial->iface, &p->cam, speed, speed) != VISCA_SUCCESS)
		return VISCA_FAILURE;

	p->pos_changing = true;
	return VISCA_SUCCESS;
}

int ptz_up(ptz_t *ptz, int speed)
{
	Ptz *p = (Ptz*)ptz;
	if (VISCA_set_pantilt_up(&p->serial->iface, &p->cam, speed, speed) != VISCA_SUCCESS)
		return VISCA_FAILURE;

	p->pos_changing = true;
	return VISCA_FAILURE;
}

int ptz_down(ptz_t *ptz, int speed)
{
	Ptz *p = (Ptz*)ptz;
	if (VISCA_set_pantilt_down(&p->serial->iface, &p->cam, speed, speed) != VISCA_SUCCESS)
		return VISCA_FAILURE;

	p->pos_changing = true;
	return VISCA_SUCCESS;
}

int ptz_get_pos(ptz_t *ptz, int *x, int *y)
{
	Ptz *p = (Ptz*)ptz;
	std::stringstream ss;
	ss << __FUNCTION__ << ':' << p->serial->iface.name;
	TimeUsed tu(ss.str().c_str());
	if (VISCA_get_pantilt_position(&p->serial->iface, &p->cam, x, y) != VISCA_SUCCESS)
		return VISCA_FAILURE;

	return VISCA_SUCCESS;
}

int ptz_set_pos(ptz_t *ptz, int x, int y, int sx = 5, int sy = 5)
{
	Ptz *p = (Ptz*)ptz;
	std::stringstream ss;
	ss << __FUNCTION__ << ':' << p->serial->iface.name;
	TimeUsed tu(ss.str().c_str());
	if (VISCA_set_pantilt_absolute_position_without_reply(&p->serial->iface, &p->cam, sx, sy, x, y) != VISCA_SUCCESS)
		return VISCA_FAILURE;

	return VISCA_SUCCESS;
}

int ptz_set_pos_with_reply(ptz_t *ptz, int x, int y, int sx, int sy)
{
	Ptz *p = (Ptz*)ptz;
	std::stringstream ss;
	ss << __FUNCTION__ << ':' << p->serial->iface.name;
	TimeUsed tu(ss.str().c_str());
	if (VISCA_set_pantilt_absolute_position(&p->serial->iface, &p->cam, sx, sy, x, y) != VISCA_SUCCESS)
		return VISCA_FAILURE;

	return VISCA_SUCCESS;
}


int ptz_set_zoom(ptz_t *ptz, int z)
{
	Ptz *p = (Ptz*)ptz;
	std::stringstream ss;
	ss << __FUNCTION__ << ':' << p->serial->iface.name;
	TimeUsed tu(ss.str().c_str());
	if (VISCA_set_zoom_value_without_reply(&p->serial->iface, &p->cam, z) != VISCA_SUCCESS)
		return VISCA_FAILURE;

	return VISCA_SUCCESS;
}

int ptz_set_zoom_with_reply(ptz_t *ptz, int z)
{
	Ptz *p = (Ptz*)ptz;
	std::stringstream ss;
	ss << __FUNCTION__ << ':' << p->serial->iface.name;
	TimeUsed tu(ss.str().c_str());
	if (VISCA_set_zoom_value(&p->serial->iface, &p->cam, z) != VISCA_SUCCESS)
		return VISCA_FAILURE;

	return VISCA_SUCCESS;
}

int ptz_get_zoom(ptz_t *ptz, int *z)
{
	Ptz *p = (Ptz*)ptz;
	std::stringstream ss;
	ss << __FUNCTION__ << ':' << p->serial->iface.name;
	TimeUsed tu(ss.str().c_str());	int v1;
	uint16_t v;
	
	if (VISCA_get_zoom_value(&p->serial->iface, &p->cam, &v) != VISCA_SUCCESS) {
		return -1;
	}
	*z = v;
	return VISCA_SUCCESS;
}

int ptz_preset_save(ptz_t *ptz, int id)
{
	Ptz *p = (Ptz*)ptz;
	return VISCA_memory_set_without_reply(&p->serial->iface, &p->cam, id);
}

int ptz_preset_call(ptz_t *ptz, int id)
{
	Ptz *p = (Ptz*)ptz;
	return VISCA_memory_recall_without_reply(&p->serial->iface, &p->cam, id);
}

int ptz_preset_clear(ptz_t *ptz, int id)
{
	Ptz *p = (Ptz*)ptz;
	return VISCA_memory_reset_without_reply(&p->serial->iface, &p->cam, id);
}

int ptz_zoom_tele(ptz_t *ptz, int s)
{
	Ptz *p = (Ptz*)ptz;

	if (VISCA_set_zoom_tele_speed(&p->serial->iface, &p->cam, s) != VISCA_SUCCESS)
		return VISCA_FAILURE;
	return VISCA_FAILURE;

}

int ptz_zoom_wide(ptz_t *ptz, int s)
{ 
	Ptz *p = (Ptz *)ptz;

	if (VISCA_set_zoom_wide_speed(&p->serial->iface, &p->cam, s) != VISCA_SUCCESS)
		return VISCA_FAILURE;

	return VISCA_SUCCESS;

}

int ptz_zoom_stop(ptz_t *ptz)
{
	Ptz *p = (Ptz*)ptz;

	if (VISCA_set_zoom_stop(&p->serial->iface, &p->cam) != VISCA_SUCCESS)
		return VISCA_FAILURE;

	return VISCA_SUCCESS;
}

int ptz_mouse_trace(ptz_t *ptz, double hvs, double vvs, int sx, int sy)
{
	fprintf(stdout, "hvs = %f, vvs = %f\n", hvs, vvs);
	Ptz *p = (Ptz*)ptz; 

	if (!p->cfg) {
		fprintf(stdout, "no configuration file\n");
		return -1;
	}

	double HVA = atof(p->cfg->get_value("hva", "55.2"));
	double VVA = atof(p->cfg->get_value("vva", "42.1"));

	fprintf(stdout, "HVA = %f, VVA = %f\n", HVA, VVA);

	int zv;
	if (ptz_get_zoom(ptz, &zv) != 0)
		return -1;
	fprintf(stdout, "zv = %d\n", zv);
	int zs = ptz_ext_get_scals(ptz, zv);
	fprintf(stdout, "zs = %d\n", zs);

	double hva = HVA / zs;
	double vva = VVA / zs;

	int h_rpm = (int)(hva*(hvs-0.5) / 0.075);
	int v_rpm = (int)(vva*(0.5-vvs) /0.075);
	fprintf(stdout, "h_rpm = %d, v_rpm = %d\n", h_rpm, v_rpm);
	return VISCA_set_pantilt_relative_position(&p->serial->iface, &p->cam , sx, sy, h_rpm, v_rpm);
}

double ptz_ext_get_scals(ptz_t *ptz, int z)
{
	Ptz *p = (Ptz*)ptz;
	if (p->zvc) {
		if (z < 0) {
			if (ptz_get_zoom(ptz, &z) < 0)
				return 1.0;
		}

		return p->zvc->mp_zoom(z);
	}
	else
		return 1.0;
}

int is_prepared(ptz_t *ptz)
{
	uint8_t power;
	Ptz *p = (Ptz*)ptz;
	return VISCA_get_power(&p->serial->iface, &p->cam, &power);
}



