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
//#   include "../../3rd/libvisca-1.1.0/visca/libvisca.h"
#	include <Windows.h>
#else
#	include <visca/libvisca.h>
#endif 
#include "ptz.h"
#include "ZoomValueConvert.h"

#include "visca.h"

#ifdef WIN32
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

static DWORD _tls_idx;

namespace {
	struct Serial;
	struct Ptz
	{
		Serial *serial;
		int addr;
		//VISCACamera_t cam;
		bool pos_changing, first_get_pos;
		int last_x, last_y;
		int set_posing;	// set_pos() 非常耗时，需要连续 get_pos() 不变后，才认为到位了
		

		ZoomValueConvert *zvc;
		KVConfig *cfg;

		std::string cfg_fname;
		std::string serial_name;
	};

	struct Serial
	{
	public:
		Serial()
		{
			ref = 0;
			vs = 0;
		}

		//VISCAInterface_t iface;
		std::vector<Ptz*> cams;

		int ref;

		visca_serial_t *vs;
	};

	typedef std::map<std::string, Serial*> SERIALS;
	static SERIALS _serials;
};

enum {
	ERR_OK = 0,
	ERR_SERIAL = -1,		// 无法打开串口.
	ERR_PTZ_NOT_EXIST = -2,	// 找不到云台.
	ERR_INVALID_PARAMS = -3,
	ERR_ADDR_OVERFLOW = -4,	// 没有这个地址的云台.
};

/// 线程相关存储.
struct thread_vars
{
	int last_err;	// 云台操作的最后错误值.
};

BOOL WINAPI DllMain(HINSTANCE hinst, DWORD r, LPVOID p)
{
	switch (r) {
	case DLL_PROCESS_ATTACH:
		_tls_idx = TlsAlloc();
		{
			thread_vars *vars = (thread_vars*)malloc(sizeof(thread_vars));
			TlsSetValue(_tls_idx, vars);
		}
		break;

	case DLL_PROCESS_DETACH:
		{
			void *p = TlsGetValue(_tls_idx);
			free(p);
		}
		TlsFree(_tls_idx);
		break;

	case DLL_THREAD_ATTACH:
		{
			thread_vars *vars = (thread_vars*)malloc(sizeof(thread_vars));
			TlsSetValue(_tls_idx, vars);
		}
		break;

	case DLL_THREAD_DETACH:
		{
			void *p = TlsGetValue(_tls_idx);
			free(p);
		}
		break;
	}

	return TRUE;
}

static void set_last_error(int err)
{
	thread_vars *vars = (thread_vars*)TlsGetValue(_tls_idx);
	vars->last_err = err;
}

static int get_last_error()
{
	thread_vars *vars = (thread_vars*)TlsGetValue(_tls_idx);
	return vars->last_err;
}

int ptz_last_error()
{
	return get_last_error();
}

ptz_t *ptz_open(const char *name, int addr)
{
	fprintf(stderr, "DEBUG: %s: try to open serial name: %s, addr=%d\n", __FUNCTION__, name, addr);

	if (!name) {
		set_last_error(ERR_INVALID_PARAMS);
		return 0;
	}

	if (addr > 7 || addr < 0) {
		set_last_error(ERR_INVALID_PARAMS);
		return 0;
	}

	return ptz2_open(name, addr);
}

ptz_t *ptz_open_with_config(const char *cfg_name)
{
	fprintf(stderr, "DEBUG: %s: cfg_name=%s\n", __FUNCTION__, cfg_name);

	return ptz2_open_with_config(cfg_name);
}

void ptz_close(ptz_t *ptz)
{
	return ptz2_close(ptz);
}

int ptz_stop(ptz_t *ptz)
{
	return ptz2_stop(ptz);
}

int ptz_left(ptz_t *ptz, int speed)
{
	return ptz2_left(ptz, speed);
}

int ptz_right(ptz_t *ptz, int speed)
{
	return ptz2_right(ptz, speed);
}

int ptz_up(ptz_t *ptz, int speed)
{
	return ptz2_up(ptz, speed);
}

int ptz_down(ptz_t *ptz, int speed)
{
	return ptz2_down(ptz, speed);
}


int ptz_get_pos(ptz_t *ptz, int *x, int *y)
{
	return ptz2_get_pos(ptz, x, y);
}

int ptz_set_pos(ptz_t *ptz, int x, int y, int sx, int sy)
{
	return ptz2_set_pos(ptz, x, y, sx, sy);
}

int ptz_set_relative_pos(ptz_t *ptz, int x, int y, int sx, int sy)
{
	return ptz2_set_relative_pos(ptz, x, y, sx, sy);
}

int ptz_set_pos_with_reply(ptz_t *ptz, int x, int y, int sx, int sy)
{
	return ptz2_set_pos_with_reply(ptz, x, y, sx, sy);
}

int ptz_set_zoom(ptz_t *ptz, int z)
{
	return ptz2_set_zoom(ptz, z);
}

int ptz_set_zoom_with_reply(ptz_t *ptz, int z)
{
	return ptz2_set_zoom_with_reply(ptz, z);
}

int ptz_get_zoom(ptz_t *ptz, int *z)
{
	return ptz2_get_zoom(ptz, z);
}

int ptz_preset_save(ptz_t *ptz, int id)
{
	return ptz2_preset_save(ptz, id);
}

int ptz_preset_call(ptz_t *ptz, int id)
{
	return ptz2_preset_call(ptz, id);
}

int ptz_preset_clear(ptz_t *ptz, int id)
{
	return ptz2_preset_clear(ptz, id);
}

int ptz_zoom_tele(ptz_t *ptz, int s)
{
	return ptz2_zoom_tele(ptz, s);
}

int ptz_zoom_wide(ptz_t *ptz, int s)
{ 
	return ptz2_zoom_wide(ptz, s);
}

int ptz_zoom_stop(ptz_t *ptz)
{
	return ptz2_zoom_stop(ptz);
}

int ptz_mouse_trace(ptz_t *ptz, double hvs, double vvs, int sx, int sy)
{
	Ptz *p = (Ptz*)ptz; 

	if (!p->cfg) {
		return -1;
	}

	double HVA = atof(p->cfg->get_value("hva", "55.2"));
	double VVA = atof(p->cfg->get_value("vva", "42.1"));

	int zv;
	if (ptz_get_zoom(ptz, &zv) != 0)
		return -1;

	double zs = ptz_ext_get_scals(ptz, zv);
	double hva = HVA / zs;
	double vva = VVA / zs;

	int h_rpm = (int)(hva*(hvs-0.5) / 0.075);
	int v_rpm = (int)(vva*(0.5-vvs) /0.075);

	return ptz_set_relative_pos(ptz, h_rpm, v_rpm, sx, sy);
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
	int z;
	if (ptz_get_zoom(ptz, &z) < 0) {
		return -1;
	}
	return 0;
}

/////////////////////////////////////////////////////////////////////////////////////////////////////////////

static SERIALS _serials2;

ptz_t *ptz2_open(const char *name, int addr)
{
	SERIALS::iterator it = _serials2.find(name);
	if (it == _serials2.end()) {
		int err;
		visca_serial_t *vs = visca_open_serial(name, &err);
		if (!vs) {
			set_last_error(-1);
			fprintf(stderr, "[ptz][%s]: %s: open %s fault!\n", name, __FUNCTION__, name);
			return 0;
		}
		
		int m;
		if (visca_set_address(vs, &m) < 0) {
			fprintf(stderr, "[ptz][%s]: %s: can't get cam nums\n", name, __FUNCTION__);
			set_last_error(-2);
			return 0;
		}

		fprintf(stderr, "[ptz][%s]: %s There are %d cams\n", name, __FUNCTION__, m);

		Serial *s = new Serial;
		s->vs = vs;
		_serials2[name] = s;

		/// prepare addrs 
		for (int i = 0; i <= m; i++) {
			Ptz *p = new Ptz;
			if (i == 0) {
				p->addr = 1;	// 当外部传递 addr=0 时，使用 1
			}
			else {
				p->addr = addr;
			}

			p->serial = s;
			p->serial_name = name;
			p->cfg = 0;
			p->zvc = 0;

			s->cams.push_back(p);
		}

		return ptz2_open(name, addr);
	}
	else {
		Serial *s = it->second;
		
		if (addr >= s->cams.size()) {
			fprintf(stderr, "[ptz][%s]: %s: invalid addr, using 1..%d\n", visca_name(s->vs), __FUNCTION__, s->cams.size()-1);
			set_last_error(-4);
			return 0;
		}
		else {
			set_last_error(0);
			s->ref++;
			return (ptz_t*)s->cams[addr];
		}
	}
}

ptz_t *ptz2_open_with_config(const char *cfg_name)
{
	fprintf(stderr, "DEBUG: %s: cfg_name=%s\n", __FUNCTION__, cfg_name);

	KVConfig *cfg = new KVConfig(cfg_name);
	
	const char *serial_name = cfg->get_value("ptz_serial_name", "COMX");
	int addr = atoi(cfg->get_value("ptz_addr", "1"));

	ptz_t *p = ptz2_open(serial_name, addr);
	if (p) {
		Ptz *ptz = (Ptz*)p;
		ptz->cfg_fname = cfg_name;
		ptz->cfg = cfg;
		ptz->zvc = new ZoomValueConvert(ptz->cfg);
	}

	fprintf(stderr, "DEBUG: %s: ret %p\n", __FUNCTION__, p);
	return p;
}

void ptz2_close(ptz_t *ptz)
{
	Ptz *p = (Ptz*)ptz;
	if (!p) {
		return;
	}

	delete p->cfg;
	delete p->zvc;

	p->serial->ref--;
	fprintf(stderr, "[ptz][%s]: %s closing, ref=%d.\n", visca_name(p->serial->vs), __FUNCTION__, p->serial->ref);
	if (p->serial->ref == 0) {
		fprintf(stderr, "[ptz][%s]: %s closed.\n", visca_name(p->serial->vs), __FUNCTION__);
		visca_close(p->serial->vs);

		std::string name = p->serial_name;
		Serial *s = p->serial;

		for (int i = 0; i < s->cams.size(); i++) {
			delete p->serial->cams[i];
		}

		delete s;

		SERIALS::iterator it = _serials.find(name);
		if (it != _serials.end()) {
			_serials.erase(it);
		}
	}
}

int ptz2_left(ptz_t *ptz, int speed)
{
	Ptz *p = (Ptz*)ptz;
	return visca_left(p->serial->vs, p->addr, speed);
}

int ptz2_right(ptz_t *ptz, int speed)
{
	Ptz *p = (Ptz*)ptz;
	return visca_right(p->serial->vs, p->addr, speed);
}

int ptz2_up(ptz_t *ptz, int speed)
{
	Ptz *p = (Ptz*)ptz;
	return visca_up(p->serial->vs, p->addr, speed);
}

int ptz2_down(ptz_t *ptz, int speed)
{
	Ptz *p = (Ptz*)ptz;
	return visca_down(p->serial->vs, p->addr, speed);
}

int ptz2_stop(ptz_t *ptz)
{
	Ptz *p = (Ptz*)ptz;
	return visca_stop(p->serial->vs, p->addr);
}

int ptz2_set_pos(ptz_t *ptz, int x, int y, int sx, int sy)
{
	Ptz *p = (Ptz*)ptz;
	return visca_set_pos(p->serial->vs, p->addr, x, y, sx, sy, 0);
}

int ptz2_set_relative_pos(ptz_t *ptz, int x, int y, int sx, int sy)
{
	Ptz *p = (Ptz*)ptz;
	return visca_set_rpos(p->serial->vs, p->addr, x, y, sx, sy);
}

int ptz2_get_pos(ptz_t *ptz, int *x, int *y)
{
	Ptz *p = (Ptz*)ptz;
	return visca_get_pos(p->serial->vs, p->addr, x, y);
}

int ptz2_get_zoom(ptz_t *ptz, int *z)
{
	Ptz *p = (Ptz*)ptz;
	return visca_get_zoom(p->serial->vs, p->addr, z);
}

int ptz2_set_zoom(ptz_t *ptz, int z)
{
	Ptz *p = (Ptz*)ptz;
	return visca_set_zoom(p->serial->vs, p->addr, z, 0);
}

int ptz2_zoom_tele(ptz_t *ptz, int s)
{
	Ptz *p = (Ptz*)ptz;
	return visca_zoom_tele(p->serial->vs, p->addr, s);
}

int ptz2_zoom_wide(ptz_t *ptz, int s)
{
	Ptz *p = (Ptz*)ptz;
	return visca_zoom_wide(p->serial->vs, p->addr, s);
}

int ptz2_zoom_stop(ptz_t *ptz)
{
	Ptz *p = (Ptz*)ptz;
	return visca_zoom_stop(p->serial->vs, p->addr);
}

int ptz2_set_pos_with_reply(ptz_t *ptz, int x, int y, int sx, int sy)
{
	Ptz *p = (Ptz*)ptz;
	return visca_set_pos(p->serial->vs, p->addr, x, y, sx, sy, 1);
}

int ptz2_set_zoom_with_reply(ptz_t *ptz, int z)
{
	Ptz *p = (Ptz*)ptz;
	return visca_set_zoom(p->serial->vs, p->addr, z, 1);
}

int ptz2_preset_call(ptz_t *ptz, int id)
{
	Ptz *p = (Ptz*)ptz;
	return visca_preset_call(p->serial->vs, p->addr, id);
}

int ptz2_preset_save(ptz_t *ptz, int id)
{
	Ptz *p = (Ptz*)ptz;
	return visca_preset_save(p->serial->vs, p->addr, id);
}

int ptz2_preset_clear(ptz_t *ptz, int id)
{
	Ptz *p = (Ptz*)ptz;
	return visca_preset_clear(p->serial->vs, p->addr, id);
}
