#include <stdio.h>
#include <stdlib.h>
#include "KVConfig.h"
#include <vector>
#include <map>
#include <string>
#include <math.h>

#ifdef WIN32
#	define VISCA_WIN
#   include "../../3rd/libvisca-1.1.0/visca/libvisca.h"
#	include <Windows.h>
#else
#	include <visca/libvisca.h>
#endif 
#include "ptz.h"
#include "ZoomValueConvert.h"

namespace {

	struct Serial;
	struct Ptz
	{
		Serial *serial;
		int addr;
		VISCACamera_t cam;

		bool pos_changing, zoom_changed, zoom_changing, first_get_pos;
		int last_x, last_y, last_z;
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

static double ptz_zoom_ratio_of_value(double v)
{
	double zx = v/10000.0;
	double focal = 58.682*pow(zx,6) - 257.08*pow(zx,5)+
			445.88*pow(zx,4) - 369.8*pow(zx,3) +
			150.84*pow(zx,2) -18.239*zx + 4.2017;
	return focal / 4.2017;
}

ptz_t *ptz_open(const char *name, int addr)
{
	fprintf(stderr, "DEBUG: %s: try to open serial name: %s, addr=%d\n", __FUNCTION__, name, addr);

		//XXX:当 addr = 0时, 程序最后三行会出问题
	if (!name) return 0;
	if (addr > 7 || addr < 0) return 0;

	SERIALS::const_iterator itf = _serials.find(name);
	if (itf == _serials.end()) {
		Serial *serial = new Serial;
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
			ptz->zoom_changed = true;
			ptz->pos_changing = ptz->zoom_changing = false;
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
	if (VISCA_set_pantilt_stop(&p->serial->iface, &p->cam, 0, 0) == VISCA_SUCCESS) {
		p->pos_changing = false;
		return 0;
	}
	return -1;
}

int ptz_left(ptz_t *ptz, int speed)
{
	Ptz *p = (Ptz*)ptz;
	if (VISCA_set_pantilt_left(&p->serial->iface, &p->cam, speed, speed) == VISCA_SUCCESS) {
		p->pos_changing = true;
		return 0;
	}
	return -1;
}

int ptz_right(ptz_t *ptz, int speed)
{
	Ptz *p = (Ptz*)ptz;
	if (VISCA_set_pantilt_right(&p->serial->iface, &p->cam, speed, speed) == VISCA_SUCCESS) {
		p->pos_changing = true;
		return 0;
	}
	return -1;
}

int ptz_up(ptz_t *ptz, int speed)
{
	Ptz *p = (Ptz*)ptz;
	if (VISCA_set_pantilt_up(&p->serial->iface, &p->cam, speed, speed) == VISCA_SUCCESS) {
		p->pos_changing = true;
		return 0;
	}
	return -1;
}

int ptz_down(ptz_t *ptz, int speed)
{
	Ptz *p = (Ptz*)ptz;
	if (VISCA_set_pantilt_down(&p->serial->iface, &p->cam, speed, speed) == VISCA_SUCCESS) {
		p->pos_changing = true;
		return 0;
	}
	return -1;
}

int ptz_get_pos(ptz_t *ptz, int *x, int *y)
{
	Ptz *p = (Ptz*)ptz;
	if (VISCA_get_pantilt_position(&p->serial->iface, &p->cam, x, y) == VISCA_SUCCESS) 
		return 0;
	else {
		fprintf(stdout, "ptz_get_pos is failure\n");
		return -1;
	}
	/*
	if (p->set_posing > 0) {
		// 此时说明 set_pos() 刚刚调用, 需要连续检查 pos 是否变化 ..
		if (VISCA_get_pantilt_position(&p->serial->iface, &p->cam, x, y) == VISCA_SUCCESS) {
			if (p->last_x == *x && p->last_y == *y) {
				p->set_posing --;
				return 0;
			}
			else {
				p->last_x = *x, p->last_y = *y;
				return 0;
			}
		}
		else {
			return -1;
		}
	}
	else {
		if (!p->set_posing && !p->first_get_pos) {
			// 返回上次 ...
			*x = p->last_x, *y = p->last_y;
			return 0;
		}
		else {
			if (VISCA_get_pantilt_position(&p->serial->iface, &p->cam, x, y) == VISCA_SUCCESS) {
				p->first_get_pos = false;
				*x = p->last_x, *y = p->last_y;
				return 0;
			}
			else {
				return -1;
			}
		}
	}*/
}

int ptz_set_pos(ptz_t *ptz, int x, int y, int sx = 5, int sy = 5)
{
	Ptz *p = (Ptz*)ptz;
	//if (VISCA_set_pantilt_absolute_position(&p->serial->iface, &p->cam, sx, sy, x, y) == VISCA_SUCCESS) {
	if (VISCA_set_pantilt_absolute_position_without_reply(&p->serial->iface, &p->cam, sx, sy, x, y) == VISCA_SUCCESS) {
		//p->set_posing = 3;	// 连续N次 get_pos() 不变才认为完成了 
		//p->pos_changing = true;
		fprintf(stderr, "%s calling\n", __FUNCTION__);
		return 0;
	}
	return -1;
}

int ptz_set_zoom(ptz_t *ptz, int z)
{
	Ptz *p = (Ptz*)ptz;
	if (VISCA_set_zoom_value(&p->serial->iface, &p->cam, z) == VISCA_SUCCESS) {
		p->zoom_changed = true;
		return 0;
	}
	return -1;
}

int ptz_get_zoom(ptz_t *ptz, int *z)
{
	Ptz *p = (Ptz*)ptz;
	uint16_t v;

	if (p->zoom_changing) {
		if (VISCA_get_zoom_value(&p->serial->iface, &p->cam, &v) == VISCA_SUCCESS) {
			*z = (short)v;
			return 0;
		}
		else {
			return -1;
		}
	}

	if (!p->zoom_changed) {
		*z = p->last_z;
		return 0;
	}

	if (VISCA_get_zoom_value(&p->serial->iface, &p->cam, &v) == VISCA_SUCCESS) {
		*z = (short)v;
		p->last_z = *z;
		p->zoom_changed = false;
		return 0;
	}
	return -1;
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

	if (VISCA_set_zoom_tele_speed(&p->serial->iface, &p->cam, s) == VISCA_SUCCESS) {
		p->zoom_changing = true;
		p->zoom_changed = true;
		return 0;
	}
	else {
		return -1;
	}
}

int ptz_zoom_wide(ptz_t *ptz, int s)
{
	Ptz *p = (Ptz *)ptz;

	if (VISCA_set_zoom_wide_speed(&p->serial->iface, &p->cam, s) == VISCA_SUCCESS) {
		p->zoom_changing = true;
		p->zoom_changed = true;
		return 0;
	}
	else {
		return -1;
	}
}

int ptz_zoom_stop(ptz_t *ptz)
{
	Ptz *p = (Ptz*)ptz;

	if (VISCA_set_zoom_stop(&p->serial->iface, &p->cam) == VISCA_SUCCESS) {
		p->zoom_changing = false;
		return 0;
	}
	else {
		return -1;
	}
}

int ptz_mouse_trace(ptz_t *ptz, int x, int y, int sx = 5, int sy = 5)
{
	Ptz *p = (Ptz*)ptz; 

	if (!p->cfg)
		return -1;	// 必须使用 ptz_open_with_config() 

	int WIDTH = atoi(p->cfg->get_value("width", "960"));
	int HEIGHT = atoi(p->cfg->get_value("height", "540"));
	double CCD_WIDTH = atof(p->cfg->get_value("ccd_width", "4.8"));
	double CCD_HEIGHT = atof(p->cfg->get_value("ccd_height", "2.7"));
	double F = atof(p->cfg->get_value("f", "4.2017"));

	double hr = double(x - WIDTH/2) / WIDTH;
	fprintf(stdout, "hr = %f\n", hr);
	double vr = double(y - HEIGHT/2) / HEIGHT;
	fprintf(stdout, "vr=%f\n", vr);
	int zv;
	if (ptz_get_zoom(ptz, &zv) != 0)
		return -1;
	fprintf(stdout, "zv = %d\n", zv);
	double zr = ptz_zoom_ratio_of_value(zv);
	fprintf(stdout, "zr=%f\n", zr);
	double f = zr * F;
	fprintf(stdout, "f = %f\n", f);
	double hh = atan(CCD_WIDTH*hr / f);
	double vv = atan(CCD_HEIGHT*vr /f);
	fprintf(stdout, "hh = %f, vv = %f\n", hh, vv);
	int h = (int)(hh/0.075);
	int v = (int)(vv/0.075);
	fprintf(stdout, "h = %d, v = %d\n", h, v);
	return VISCA_set_pantilt_relative_position(&p->serial->iface, &p->cam , sx, sy, h, v);
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
