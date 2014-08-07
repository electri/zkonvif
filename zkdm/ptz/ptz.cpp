#include <stdio.h>
#include <stdlib.h>
#include <vector>
#include <map>
#include <string>
#ifdef WIN32
#	define VISCA_WIN
#	include "../win32/zkptz/zkptz/libvisca.h"
#else
#	include <visca/libvisca.h>
#endif 
#include "ptz.h"

namespace {

	struct Serial;
	struct Ptz
	{
		Serial *serial;
		int addr;
		VISCACamera_t cam;

		bool pos_changed, zoom_changed;
		int last_x, last_y, last_z;
		int set_posing;	// set_pos() 非常耗时，需要连续 get_pos() 不变后，才认为到位了
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
	if (!name) return 0;
	if (addr > 7 || addr < 0) return 0;

	SERIALS::const_iterator itf = _serials.find(name);
	if (itf == _serials.end()) {
		Serial *serial = new Serial;
		if (VISCA_open_serial(&serial->iface, name) == VISCA_FAILURE) {
			fprintf(stderr, "ERR: %s: can't open '%s'\n", __func__, name);
			_serials[name] = serial; // 下次没有必要再试了 ..
			return 0;
		}

		serial->iface.broadcast = 0;

		for (int i = 0; i < 7; i++) {
			Ptz *ptz = new Ptz;
			ptz->pos_changed = ptz->zoom_changed = true;
			ptz->set_posing = 1;
			ptz->serial = serial;
			ptz->addr = i+1;
			ptz->cam.address = ptz->addr;

			if (i == 0)
				serial->cams.push_back(ptz);
			serial->cams.push_back(ptz);
		}

		_serials[name] = serial;
		return ptz_open(name, addr);
	}
	else {
		Serial *serial = itf->second;
		if (addr > serial->cams.size()) {
			fprintf(stderr, "ERROR: %s: addr=%d but range=[1..%d]\n", __func__, addr, itf->second->cams.size());
			return 0;
		}
		
		return (ptz_t*)serial->cams[addr];
	}
}

void ptz_close(ptz_t *ptz)
{
	// TODO: 应该根据串口的引用计数关闭 ...
	Ptz *p = (Ptz*)ptz;
	VISCA_close_serial(&p->serial->iface);

}

int ptz_stop(ptz_t *ptz)
{
	Ptz *p = (Ptz*)ptz;
	if (VISCA_set_pantilt_stop(&p->serial->iface, &p->cam, 0, 0) == VISCA_SUCCESS) {
		p->pos_changed = false;
		return 0;
	}
	return -1;
}

int ptz_left(ptz_t *ptz, int speed)
{
	Ptz *p = (Ptz*)ptz;
	if (VISCA_set_pantilt_left(&p->serial->iface, &p->cam, speed, speed) == VISCA_SUCCESS) {
		p->pos_changed = true;
		return 0;
	}
	return -1;
}

int ptz_right(ptz_t *ptz, int speed)
{
	Ptz *p = (Ptz*)ptz;
	if (VISCA_set_pantilt_right(&p->serial->iface, &p->cam, speed, speed) == VISCA_SUCCESS) {
		p->pos_changed = true;
		return 0;
	}
	return -1;
}

int ptz_up(ptz_t *ptz, int speed)
{
	Ptz *p = (Ptz*)ptz;
	if (VISCA_set_pantilt_up(&p->serial->iface, &p->cam, speed, speed) == VISCA_SUCCESS) {
		p->pos_changed = true;
		return 0;
	}
	return -1;
}

int ptz_down(ptz_t *ptz, int speed)
{
	Ptz *p = (Ptz*)ptz;
	if (VISCA_set_pantilt_down(&p->serial->iface, &p->cam, speed, speed) == VISCA_SUCCESS) {
		p->pos_changed = true;
		return 0;
	}
	return -1;
}

int ptz_get_pos(ptz_t *ptz, int *x, int *y)
{
	Ptz *p = (Ptz*)ptz;

/*
	if (p->set_posing > 0) {
		fprintf(stderr, "%s: set_posing=%d\n", __func__, p->set_posing);

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
		else
			return -1;
	}

	if (!p->pos_changed) {
		fprintf(stderr, "%s: pos_changed ...\n", __func__);
		*x = p->last_x, *y = p->last_y;
		return 0;
	}
*/
	VISCA_get_pantilt_position(&p->serial->iface, &p->cam, x, y);
	if (VISCA_get_pantilt_position(&p->serial->iface, &p->cam, x, y) == VISCA_SUCCESS) {
		p->last_x = *x, p->last_y = *y;
		return 0;
	}

	return -1;
}

int ptz_set_pos(ptz_t *ptz, int x, int y, int sx, int sy)
{
	Ptz *p = (Ptz*)ptz;
	if (VISCA_set_pantilt_absolute_position_without_reply(&p->serial->iface, &p->cam, sx, sy, x, y) == VISCA_SUCCESS) {
		p->set_posing = 5;	// 连续5次 get_pos() 不变才认为完成了 
		p->pos_changed = true;
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
