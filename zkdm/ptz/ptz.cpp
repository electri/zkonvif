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
		VISCACamera_t cam;
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

		VISCAInterface_t iface;
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

		//XXX:当 addr = 0时, 程序最后三行会出问题 
	if (!name) {
		set_last_error(ERR_INVALID_PARAMS);
		return 0;
	}

	if (addr > 7 || addr < 0) {
		set_last_error(ERR_INVALID_PARAMS);
		return 0;
	}

	SERIALS::const_iterator itf = _serials.find(name);
	if (itf == _serials.end()) {
		Serial *serial = new Serial;
		_snprintf(serial->iface.name, sizeof(serial->iface.name), "%s", name);
		if (VISCA_open_serial(&serial->iface, name) == VISCA_FAILURE) {
			printf("ERR: %s: can't open '%s'\n", __func__, name);
			set_last_error(ERR_SERIAL);
			return 0;
		}

		int m;
		if (VISCA_set_address(&serial->iface, &m) == VISCA_FAILURE) {
			printf("ERR: %s: set_address fault!\n", __func__);
			set_last_error(ERR_PTZ_NOT_EXIST);
			VISCA_close_serial(&serial->iface);
			return 0;
		}

		fprintf(stdout, "DEBUG: %s: %s: has %d ptzs\n", __FUNCTION__, name, m);
		
		serial->iface.broadcast = 0;

		// 存在 m 个云台.
		// FIXME: 这里认为 0 和 1 是一个吧 :)
		for (int i = 0; i <= m; i++) {
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

		if (addr >= serial->cams.size()) {
			fprintf(stderr, "ERR: %s: there are %d cams, addr overflow!!!\n", __func__, serial->cams.size());
			set_last_error(ERR_ADDR_OVERFLOW);
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
			ptz->serial_name = name;

			serial->cams[addr] = ptz;
	
			serial->ref++;

			fprintf(stderr, "INFO: %s: %s:%d opened!\n", __func__, name, addr);
		}
		else {
			fprintf(stderr, "WARNING: %s: ptz has been opened!!!\n", __FUNCTION__);
		}

		set_last_error(ERR_OK);

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
		ptz->cfg_fname = cfg_name;
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
	if (!p) return;

	fprintf(stderr, "INFO: %s calling\n", __func__);

	delete p->cfg;
	delete p->zvc;

	p->serial->ref--;

	if (p->serial->ref == 0) {
		VISCA_close_serial(&p->serial->iface);
		
		for (SERIALS::iterator it = _serials.begin(); it != _serials.end(); ++it) {
			if (it->second->ref == 0) {
				fprintf(stderr, "INFO: %s: serial %s closed!\n", __func__, it->first.c_str());
				delete it->second;
				_serials.erase(it);
				break;
			}
		}
	}
}

int ptz_stop(ptz_t *ptz)
{
	Ptz *p = (Ptz*)ptz;
	std::stringstream ss;
	ss << __FUNCTION__ << ':' << p->serial->iface.name;
	TimeUsed tu(ss.str().c_str());
	if (VISCA_set_pantilt_stop_without_reply(&p->serial->iface, &p->cam, 0, 0) != VISCA_SUCCESS)
		return VISCA_FAILURE;
	Sleep(20);
	p->pos_changing = false;
	return VISCA_SUCCESS;
}

int ptz_left(ptz_t *ptz, int speed)
{
	Ptz *p = (Ptz*)ptz;
	if (VISCA_set_pantilt_left_without_reply(&p->serial->iface, &p->cam, speed, speed) != VISCA_SUCCESS)
		return VISCA_FAILURE;
	Sleep(20);
	p->pos_changing = true;
	return VISCA_SUCCESS;
}

int ptz_right(ptz_t *ptz, int speed)
{
	Ptz *p = (Ptz*)ptz;
	if (VISCA_set_pantilt_right_without_reply(&p->serial->iface, &p->cam, speed, speed) != VISCA_SUCCESS)
		return VISCA_FAILURE;
	Sleep(20);
	p->pos_changing = true;
	return VISCA_SUCCESS;
}

int ptz_up(ptz_t *ptz, int speed)
{
	Ptz *p = (Ptz*)ptz;
	if (VISCA_set_pantilt_up_without_reply(&p->serial->iface, &p->cam, speed, speed) != VISCA_SUCCESS)
		return VISCA_FAILURE;
	Sleep(20);
	p->pos_changing = true;
	return VISCA_FAILURE;
}

int ptz_down(ptz_t *ptz, int speed)
{
	Ptz *p = (Ptz*)ptz;
	if (VISCA_set_pantilt_down_without_reply(&p->serial->iface, &p->cam, speed, speed) != VISCA_SUCCESS)
		return VISCA_FAILURE;
	Sleep(20);
	p->pos_changing = true;
	return VISCA_SUCCESS;
}


int ptz_get_pos(ptz_t *ptz, int *x, int *y)
{
	Ptz *p = (Ptz*)ptz;
	std::stringstream ss;
	ss << __FUNCTION__ << ':' << p->serial->iface.name;
	TimeUsed tu(ss.str().c_str());
	if (PurgeComm(p->serial->iface.port_fd, PURGE_RXCLEAR) == 0) {
		return VISCA_FAILURE;
	}
	if (VISCA_get_pantilt_position(&p->serial->iface, &p->cam, x, y) != VISCA_SUCCESS)
		return VISCA_FAILURE;

	return VISCA_SUCCESS;
}

int ptz_set_pos(ptz_t *ptz, int x, int y, int sx, int sy)
{
	Ptz *p = (Ptz*)ptz;
	std::stringstream ss;
	ss << __FUNCTION__ << ':' << p->serial->iface.name;
	TimeUsed tu(ss.str().c_str());
	if (VISCA_set_pantilt_absolute_position_without_reply(&p->serial->iface, &p->cam, sx, sy, x, y) != VISCA_SUCCESS)
		return VISCA_FAILURE;
	Sleep(20);
	return VISCA_SUCCESS;
}

int ptz_set_relative_pos(ptz_t *ptz, int x, int y, int sx, int sy)
{
	Ptz *p = (Ptz*)ptz;
	std::stringstream ss;
	ss << __FUNCTION__ << ':' << p->serial->iface.name;
	TimeUsed tu(ss.str().c_str());
	if (VISCA_set_pantilt_relative_position_without_reply(&p->serial->iface, &p->cam, sx, sy, x, y) != VISCA_SUCCESS)
		return VISCA_FAILURE;
	Sleep(20);
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
	Sleep(20);
	return VISCA_SUCCESS;
}

int ptz_set_zoom_with_reply(ptz_t *ptz, int z)
{
	Ptz *p = (Ptz*)ptz;
	std::stringstream ss;
	ss << __FUNCTION__ << ':' << p->serial->iface.name;
	TimeUsed tu(ss.str().c_str());
	if (VISCA_set_zoom_value_without_reply(&p->serial->iface, &p->cam, z) != VISCA_SUCCESS)
		return VISCA_FAILURE;
	Sleep(20);
	return VISCA_SUCCESS;
}

int ptz_get_zoom(ptz_t *ptz, int *z)
{
	Ptz *p = (Ptz*)ptz;
	std::stringstream ss;
	ss << __FUNCTION__ << ':' << p->serial->iface.name;
	TimeUsed tu(ss.str().c_str());	int v1;
	uint16_t v;
	if (PurgeComm(p->serial->iface.port_fd, PURGE_RXCLEAR) == 0) {
		return VISCA_FAILURE;
	}
	if (VISCA_get_zoom_value(&p->serial->iface, &p->cam, &v) != VISCA_SUCCESS) {
		return -1;
	}
	*z = v;
	return VISCA_SUCCESS;
}

int ptz_preset_save(ptz_t *ptz, int id)
{
	Ptz *p = (Ptz*)ptz;
	if (VISCA_memory_set_without_reply(&p->serial->iface, &p->cam, id) != VISCA_SUCCESS)
		return VISCA_FAILURE;
	Sleep(20);
	return VISCA_SUCCESS;
}

int ptz_preset_call(ptz_t *ptz, int id)
{
	Ptz *p = (Ptz*)ptz;
	if (VISCA_memory_recall_without_reply(&p->serial->iface, &p->cam, id) != VISCA_SUCCESS)
		return VISCA_FAILURE;
	Sleep(20);
	return VISCA_SUCCESS;
}

int ptz_preset_clear(ptz_t *ptz, int id)
{
	Ptz *p = (Ptz*)ptz;
	if (VISCA_memory_reset_without_reply(&p->serial->iface, &p->cam, id) != VISCA_SUCCESS)
		return VISCA_FAILURE;
	Sleep(20);
	return VISCA_SUCCESS;
}

int ptz_zoom_tele(ptz_t *ptz, int s)
{
	TimeUsed tu(__FUNCTION__);
	Ptz *p = (Ptz*)ptz;

	if (VISCA_set_zoom_tele_speed_without_reply(&p->serial->iface, &p->cam, s) != VISCA_SUCCESS)
		return VISCA_FAILURE;
	Sleep(20);
	return VISCA_FAILURE;

}

int ptz_zoom_wide(ptz_t *ptz, int s)
{ 
	Ptz *p = (Ptz *)ptz;

	if (VISCA_set_zoom_wide_speed_without_reply(&p->serial->iface, &p->cam, s) != VISCA_SUCCESS)
		return VISCA_FAILURE;
	Sleep(20);
	return VISCA_SUCCESS;

}

int ptz_zoom_stop(ptz_t *ptz)
{
	Ptz *p = (Ptz*)ptz;

	if (VISCA_set_zoom_stop_without_reply(&p->serial->iface, &p->cam) != VISCA_SUCCESS)
		return VISCA_FAILURE;
	Sleep(20);
	return VISCA_SUCCESS;
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
	if (VISCA_set_pantilt_relative_position_without_reply(&p->serial->iface, &p->cam , sx, sy, h_rpm, v_rpm) != VISCA_SUCCESS) 
		return VISCA_FAILURE;

	Sleep(20);
	return VISCA_SUCCESS;
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
	if (PurgeComm(p->serial->iface.port_fd, PURGE_RXCLEAR) == 0) {
		return VISCA_FAILURE;
	}
	if (VISCA_get_power(&p->serial->iface, &p->cam, &power) != VISCA_SUCCESS)
		return VISCA_FAILURE;
	
	return VISCA_SUCCESS;
		
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
			fprintf(stderr, "[ptz][%s]: %s: open %s fault!\n", name, __FUNCTION__, name);
			return 0;
		}
		
		int m;
		if (visca_set_address(vs, &m) < 0) {
			fprintf(stderr, "[ptz][%s]: %s: can't get cam nums\n", name, __FUNCTION__);
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
			return 0;
		}
		else {
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
