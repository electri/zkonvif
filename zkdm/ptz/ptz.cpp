#include <stdio.h>
#include <stdlib.h>
#include <vector>
#include <map>
#include <string>
#include <visca/libvisca.h>
#include "ptz.h"

namespace {

	struct Serial;
	struct Ptz
	{
		Serial *serial;
		int addr;
		VISCACamera_t cam;
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

		fprintf(stderr, "DEBUG: %s: serial opened '%s'\n", __func__, name);

#if 0
		// FIXME: 不管了，认为调用者知道有几个云台吧 ...
		// set address, 得到所有云台 ...
		int m;
		if (VISCA_set_address(&serial->iface, &m) == VISCA_FAILURE) {
			fprintf(stderr, "ERR: %s: set address for '%s'\n", __func__, name);
			VISCA_close_serial(&serial->iface);
			_serials[name] = serial;
			return 0;
		}

		fprintf(stderr, "DEBUG: %s: set address ok, m=%d\n", __func__, m);

		// 初始化所有 ...
		for (int i = 0; i < m; i++) {
			Ptz *ptz = new Ptz;
			ptz->serial = serial;
			ptz->addr = i+1;

			ptz->cam.address = ptz->addr;
			//VISCA_clear(&serial->iface, &ptz->cam);
			VISCA_get_camera_info(&serial->iface, &ptz->cam);
			fprintf(stdout, "DEBUG: %s: found ptz: addr=%d, vendor=%04x, model=%04x, rom=%04x\n",
					__func__, ptz->addr, ptz->cam.vendor, ptz->cam.model, ptz->cam.rom_version);

			if (i == 0)
				serial->cams.push_back(ptz); // 多放一个，这样 addr=0 和 1 时，都使用相同的 ..

			serial->cams.push_back(ptz);

		}
#else
		for (int i = 0; i < 7; i++) {
			Ptz *ptz = new Ptz;
			ptz->serial = serial;
			ptz->addr = i+1;
			ptz->cam.address = ptz->addr;

			if (i == 0)
				serial->cams.push_back(ptz);
			serial->cams.push_back(ptz);
		}
#endif

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
	fprintf(stderr, "=====> stop\n");
	if (VISCA_set_pantilt_stop(&p->serial->iface, &p->cam, 0, 0) == VISCA_SUCCESS)
		return 0;
	return -1;
}

int ptz_left(ptz_t *ptz, int speed)
{
	Ptz *p = (Ptz*)ptz;
	fprintf(stderr, "=====> %s: %d\n", __func__, speed);
	if (VISCA_set_pantilt_left(&p->serial->iface, &p->cam, speed, speed) == VISCA_SUCCESS)
		return 0;
	return -1;
}

int ptz_right(ptz_t *ptz, int speed)
{
	Ptz *p = (Ptz*)ptz;
	fprintf(stderr, "=====> %s: %d\n", __func__, speed);
	if (VISCA_set_pantilt_right(&p->serial->iface, &p->cam, speed, speed) == VISCA_SUCCESS)
		return 0;
	return -1;
}

int ptz_up(ptz_t *ptz, int speed)
{
	Ptz *p = (Ptz*)ptz;
	fprintf(stderr, "=====> %s: %d\n", __func__, speed);
	if (VISCA_set_pantilt_up(&p->serial->iface, &p->cam, speed, speed) == VISCA_SUCCESS)
		return 0;
	return -1;
}

int ptz_down(ptz_t *ptz, int speed)
{
	Ptz *p = (Ptz*)ptz;
	fprintf(stderr, "=====> %s: %d\n", __func__, speed);
	if (VISCA_set_pantilt_down(&p->serial->iface, &p->cam, speed, speed) == VISCA_SUCCESS)
		return 0;
	return -1;
}

int ptz_get_pos(ptz_t *ptz, int *x, int *y)
{
	Ptz *p = (Ptz*)ptz;

	fprintf(stderr, "=====> %s: calling\n", __func__);
	// FIXME: 这里必须获取两次，否则可能失败，不知道啥原因？？？ ...
	VISCA_get_pantilt_position(&p->serial->iface, &p->cam, x, y);
	if (VISCA_get_pantilt_position(&p->serial->iface, &p->cam, x, y) == VISCA_SUCCESS) {
		fprintf(stderr, "\tx=%d, y=%d\n", *x, *y);
		return 0;
	}

	fprintf(stderr, "\terror \n");
	return -1;
}

int ptz_set_pos(ptz_t *ptz, int x, int y, int sx, int sy)
{
	Ptz *p = (Ptz*)ptz;
	fprintf(stderr, "======> set pos: %d, %d, %d, %d\n", x, y, sx, sy);
	if (VISCA_set_pantilt_absolute_position(&p->serial->iface, &p->cam, sx, sy, x, y) == VISCA_SUCCESS)
		return 0;
	return -1;
}

int ptz_set_zoom(ptz_t *ptz, int z)
{
	Ptz *p = (Ptz*)ptz;
	fprintf(stderr, "=====> set zoom: %d\n", z);
	if (VISCA_set_zoom_value(&p->serial->iface, &p->cam, z) == VISCA_SUCCESS)
		return 0;
	return -1;
}

int ptz_get_zoom(ptz_t *ptz, int *z)
{
	Ptz *p = (Ptz*)ptz;
	uint16_t v;
	fprintf(stderr, "=====> get zoom: calling\n");
	VISCA_get_zoom_value(&p->serial->iface, &p->cam, &v);
	if (VISCA_get_zoom_value(&p->serial->iface, &p->cam, &v) == VISCA_SUCCESS) {
		fprintf(stderr, "... v=%u\n", v);
		*z = (short)v;
		return 0;
	}
	return -1;
}

