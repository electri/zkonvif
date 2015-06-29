#include <stdio.h>
#include <stdlib.h>
#include "visca.h"
#include "serial_win32.h"
#include <string.h>

struct visca_serial_t
{
	serial_t *serial;
	char *name;
};

/// 读取，直到收到结束符 0xff
static int get_packet(serial_t *s, void *buf, int buflen)
{
	int n;
	unsigned char *p = (unsigned char*)buf;

	for (n = 0; n < buflen; n++, p++) {
		int rc = serial_read(s, p, 1);
		if (rc < 0) {
			return -1; // read fault
		}
		else if (rc == 0) {
			// 超时
			return -3;
		}

		if (*p == 0xff) {
			return n+1;
		}
	}

	return -2;	// overflow
}

visca_serial_t *visca_open_serial(const char *name, int *err)
{
	serial_t *s = serial_open(name);
	if (!s) {
		*err = VISCA_ERR_SERIAL_OPEN;
		return 0;
	}

	visca_serial_t *vs = new visca_serial_t;
	vs->serial = s;
	vs->name = strdup(name);

	return vs;
}

void visca_close(visca_serial_t *vs)
{
	free(vs->name);
	serial_close(vs->serial);
	delete vs;
}

const char *visca_name(visca_serial_t *vs)
{
	return vs->name;
}

int visca_set_address(visca_serial_t *vs, int *num)
{
	unsigned char codes[4] = { 0x88, 0x30, 0x01, 0xff };
	if (serial_write(vs->serial, codes, 4) != 4) {
		fprintf(stderr, "[ptz][%s]: %s: write fault\n", vs->name, __FUNCTION__);
		return -1;
	}

	unsigned char res[16];
	if (get_packet(vs->serial, res, sizeof(res)) < 0) {
		fprintf(stderr, "[ptz][%s]: %s: to get set address reply fault!!!\n", vs->name, __FUNCTION__);
		return -1;
	}

	// 0x88 0x30 0x0N 0xff
	*num = (res[2] & 0x7) - 1;

	return 0;
}

enum {
	VISCA_ERR_SYNTAX = 2,
	VISCA_ERR_COMMAND_BUFFER_FULL = 3,
	VISCA_ERR_COMMAND_CANCEL = 4,
	VISCA_ERR_NO_SOCKET = 5,
	VISCA_ERR_COMMAND_NOT_EXECUTABLE = 0x41,
};

static int get_next_ack(visca_serial_t *s, int *who)
{
	for (; ; ) {
		unsigned char res[16];
		if (get_packet(s->serial, res, sizeof(res)) < 0) {
			fprintf(stderr, "[ptz][%s]: %s read ack err!\n", s->name, __FUNCTION__);
			return -1;
		}

		switch (res[1] & 0xf0) {
		case 0x40:
			if (who) {
				*who = (res[0]>>4) - 8;
			}
			return 0;
			break;

		case 0x50:
			break;

		case 0x60:
			if (*who) {
				*who = (res[0]>>4) - 8;
			}
			return res[2];	// 返回错误：
			break;

		default:
			fprintf(stderr, "[ptz][%s]: %s !!!!!!! got unknown result %02x\n", s->name, __FUNCTION__);
			break;
		}
	}

	return -1;
}

static int get_complete(visca_serial_t *s, int *who)
{
	for (; ; ) {
		unsigned char res[16];
		if (get_packet(s->serial, res, sizeof(res)) < 0) {
			fprintf(stderr, "[ptz][%s]: %s read completion err!\n", s->name, __FUNCTION__);
			return -1;
		}

		switch (res[1] & 0xf0) {
		case 0x40:
			break;

		case 0x60:
			if (*who) {
				*who = (res[0]>>4) - 8;
			}
			return res[2];	// 返回错误：

		case 0x50:
			if (res[1] != 0x50) {
				if (*who) {
					*who = (res[0]>>4) - 8;
				}
				return 0;
			}
			else {
				fprintf(stderr, "[ptz][%s]: %s !!!!!!!! got response packet???????\n", s->name, __FUNCTION__);
			}
			break;

		default:
			fprintf(stderr, "[ptz][%s]: %s !!!!!!! got unknown result %02x\n", s->name, __FUNCTION__);
			break;
		}
	}

	return -1;
}

static int get_response(visca_serial_t *s, int *who, unsigned char *res, int buflen)
{
	for (; ; ) {
		if (get_packet(s->serial, res, buflen) < 0) {
			fprintf(stderr, "[ptz][%s]: %s read response err!\n", s->name, __FUNCTION__);
			return -1;
		}

		switch (res[1] & 0xf0) {
		case 0x40:
			break;

		case 0x60:
			if (*who) {
				*who = (res[0]>>4) - 8;
			}
			return res[2];	// 返回错误
			break;

		case 0x50:
			if (res[1] == 0x50) {
				if (who) {
					*who = (res[0]>>4) - 8;
				}
				return 0;
			}
			else {
				fprintf(stderr, "[ptz][%s]: %s !!!!!! get completion packet????\n", s->name, __FUNCTION__);
			}
			break;

		default:
			fprintf(stderr, "[ptz][%s]: %s !!!!!!! got unknown result %02x\n", s->name, __FUNCTION__);
			break;
		}
	}

	return -1;
}

void print_err(int err)
{
	fprintf(stderr, "======= ERR：%d\n", err);
}

int visca_left(visca_serial_t *s, int addr, int speed)
{
	// 8x 01 06 01 VV WW 01 03 FF

	addr &= 0x7;
	unsigned char codes[9] = { 0x80 | addr, 0x01, 0x06, 0x01, speed, speed, 0x01, 0x03, 0xff };
	int n = sizeof(codes)/sizeof(unsigned char);
	if (serial_write(s->serial, codes, n) != n) {
		fprintf(stderr, "[ptz][%s]: %s write comm err!\n", s->name, __FUNCTION__);
		return -1;
	}

	int who;
	int rc = get_next_ack(s, &who);
	if (rc < 0) {
		fprintf(stderr, "[ptz][%s]: %s can't get ack\n", s->name, __FUNCTION__);
		return -1;
	}
	else if (rc) {
		print_err(rc);
		return -1000+rc;
	}

	// 不关心完成 :)

	return 0;
}

int visca_right(visca_serial_t *s, int addr, int speed)
{
	// 8x 01 06 01 VV WW 02 03 FF

	addr &= 0x7;
	unsigned char codes[9] = { 0x80 | addr, 0x01, 0x06, 0x01, speed, speed, 0x02, 0x03, 0xff };
	int n = sizeof(codes)/sizeof(unsigned char);
	if (serial_write(s->serial, codes, n) != n) {
		fprintf(stderr, "[ptz][%s]: %s write comm err!\n", s->name, __FUNCTION__);
		return -1;
	}

	int who;
	int rc = get_next_ack(s, &who);
	if (rc < 0) {
		fprintf(stderr, "[ptz][%s]: %s can't get ack\n", s->name, __FUNCTION__);
		return -1;
	}
	else if (rc) {
		print_err(rc);
		return -1000+rc;
	}

	// 不关心完成 :)

	return 0;
}

int visca_up(visca_serial_t *s, int addr, int speed)
{
	// 8x 01 06 01 VV WW 03 01 FF

	addr &= 0x7;
	unsigned char codes[9] = { 0x80 | addr, 0x01, 0x06, 0x01, speed, speed, 0x03, 0x01, 0xff };
	int n = sizeof(codes)/sizeof(unsigned char);
	if (serial_write(s->serial, codes, n) != n) {
		fprintf(stderr, "[ptz][%s]: %s write comm err!\n", s->name, __FUNCTION__);
		return -1;
	}

	int who;
	int rc = get_next_ack(s, &who);
	if (rc < 0) {
		fprintf(stderr, "[ptz][%s]: %s can't get ack\n", s->name, __FUNCTION__);
		return -1;
	}
	else if (rc) {
		print_err(rc);
		return -1000+rc;
	}

	// 不关心完成 :)

	return 0;
}

int visca_down(visca_serial_t *s, int addr, int speed)
{
	// 8x 01 06 01 VV WW 03 02 FF

	addr &= 0x7;
	unsigned char codes[9] = { 0x80 | addr, 0x01, 0x06, 0x01, speed, speed, 0x03, 0x02, 0xff };
	int n = sizeof(codes)/sizeof(unsigned char);
	if (serial_write(s->serial, codes, n) != n) {
		fprintf(stderr, "[ptz][%s]: %s write comm err!\n", s->name, __FUNCTION__);
		return -1;
	}

	int who;
	int rc = get_next_ack(s, &who);
	if (rc < 0) {
		fprintf(stderr, "[ptz][%s]: %s can't get ack\n", s->name, __FUNCTION__);
		return -1;
	}
	else if (rc) {
		print_err(rc);
		return -1000+rc;
	}

	// 不关心完成 :)

	return 0;
}

int visca_stop(visca_serial_t *s, int addr)
{
	// 8x 01 06 01 VV WW 03 03 FF

	addr &= 0x7;
	unsigned char codes[9] = { 0x80 | addr, 0x01, 0x06, 0x01, 0, 0, 0x03, 0x03, 0xff };
	int n = sizeof(codes)/sizeof(unsigned char);
	if (serial_write(s->serial, codes, n) != n) {
		fprintf(stderr, "[ptz][%s]: %s write comm err!\n", s->name, __FUNCTION__);
		return -1;
	}

	int who;
	int rc = get_next_ack(s, &who);
	if (rc < 0) {
		fprintf(stderr, "[ptz][%s]: %s can't get ack\n", s->name, __FUNCTION__);
		return -1;
	}
	else if (rc) {
		print_err(rc);
		return -1000+rc;
	}

	// 不关心完成 :)

	return 0;
}

int visca_set_pos(visca_serial_t *s, int addr, int x, int y, int sx, int sy, int wait)
{
	short xx = (short)x, yy = (short)y;
	unsigned char *px = (unsigned char*)&xx, *py = (unsigned char*)&yy;

	// 8x 01 06 02 VV WW 0Y 0Y 0Y 0Y 0Z 0Z 0Z 0Z FF
	addr &= 0x07;
	unsigned char codes[15] = { 0x80 | addr, 1, 6, 2, sx, sy, 
		px[1]>>4, px[1]&0xf, px[0]>>4, px[0]&0xf, 
		py[1]>>4, py[1]&0xf, py[0]>>4, py[0]&0xf, 
		0xff };
	int n = sizeof(codes);
	if (serial_write(s->serial, codes, n) != n) {
		fprintf(stderr, "[ptz][%s]: %s write comm err!\n", s->name, __FUNCTION__);
		return -1;
	}

	int who;
	int rc = get_next_ack(s, &who);
	if (rc < 0) {
		fprintf(stderr, "[ptz][%s]: %s can't get ack\n", s->name, __FUNCTION__);
		return -1;
	}
	else if (rc) {
		print_err(rc);
		return -1000+rc;
	}

	if (wait) {
		// 等待完成包
		rc = get_complete(s, &who);
		if (rc < 0) {
			fprintf(stderr, "[ptz][%s]: %s can't get completion\n", s->name, __FUNCTION__);
			return -1;
		}
		else if (rc) {
			print_err(rc);
			return -1000+rc;
		}
	}

	return 0;
}

int visca_set_rpos(visca_serial_t *s, int addr, int x, int y, int sx, int sy)
{
	short xx = (short)x, yy = (short)y;
	unsigned char *px = (unsigned char*)&xx, *py = (unsigned char*)&yy;

	// 8x 01 06 03 VV WW 0Y 0Y 0Y 0Y 0Z 0Z 0Z 0Z FF
	addr &= 0x07;
	unsigned char codes[15] = { 0x80 | addr, 1, 6, 3, sx, sy, 
		px[1]>>4, px[1]&0xf, px[0]>>4, px[0]&0xf, 
		py[1]>>4, py[1]&0xf, py[0]>>4, py[0]&0xf, 
		0xff };
	int n = sizeof(codes);
	if (serial_write(s->serial, codes, n) != n) {
		fprintf(stderr, "[ptz][%s]: %s write comm err!\n", s->name, __FUNCTION__);
		return -1;
	}

	int who;
	int rc = get_next_ack(s, &who);
	if (rc < 0) {
		fprintf(stderr, "[ptz][%s]: %s can't get ack\n", s->name, __FUNCTION__);
		return -1;
	}
	else if (rc) {
		print_err(rc);
		return -1000 + rc;
	}

	// 不关心完成包了 :)

	return 0;
}

int visca_get_pos(visca_serial_t *s, int addr, int *x, int *y)
{
	// 8x 09 06 12 FF
	// Y0 50 0W 0W 0W 0W 0Z 0Z 0Z 0Z FF
	addr &= 0x07;
	unsigned char codes[5] = { 0x80|addr, 9, 6, 0x12, 0xff };
	int n = sizeof(codes);
	if (serial_write(s->serial, codes, n) != n) {
		fprintf(stderr, "[ptz][%s]: %s write comm err\n!", s->name, __FUNCTION__);
		return -1;
	}

	unsigned char res[16];
	int who;
	int rc = get_response(s, &who, res, sizeof(res));
	if (rc == 0) {
		short h = 0, v = 0;
		unsigned char *ph = (unsigned char*)&h, *pv = (unsigned char*)&v;
		ph[0] = res[4]<<4 | res[5];
		ph[1] = res[2]<<4 | res[3];
		pv[0] = res[8]<<4 | res[9];
		pv[1] = res[6]<<4 | res[7];

		*x = h, *y = v;
		return 0;
	}
	else if (rc < 0) {
		fprintf(stderr, "[ptz][%s]: %s can't get response!\n", s->name, __FUNCTION__);
		return -1;
	}
	else {
		print_err(rc);
		return -1000+rc;
	}
}

int visca_zoom_tele(visca_serial_t *s, int addr, int speed)
{
	// 8x 01 04 07 2Z FF
	addr &= 0x7;
	unsigned char codes[6] = { 0x80 | addr, 1, 4, 7, 0x20|speed, 0xff };
	int n = sizeof(codes)/sizeof(unsigned char);
	if (serial_write(s->serial, codes, n) != n) {
		fprintf(stderr, "[ptz][%s]: %s write comm err!\n", s->name, __FUNCTION__);
		return -1;
	}

	int who;
	int rc = get_next_ack(s, &who);
	if (rc < 0) {
		fprintf(stderr, "[ptz][%s]: %s can't get ack\n", s->name, __FUNCTION__);
		return -1;
	}
	else if (rc) {
		print_err(rc);
		return -1000+rc;
	}

	// 不关心完成 :)

	return 0;

}

int visca_zoom_wide(visca_serial_t *s, int addr, int speed)
{
	// 8x 01 04 07 3Z FF
	addr &= 0x7;
	unsigned char codes[6] = { 0x80 | addr, 1, 4, 7, 0x30|speed, 0xff };
	int n = sizeof(codes)/sizeof(unsigned char);
	if (serial_write(s->serial, codes, n) != n) {
		fprintf(stderr, "[ptz][%s]: %s write comm err!\n", s->name, __FUNCTION__);
		return -1;
	}

	int who;
	int rc = get_next_ack(s, &who);
	if (rc < 0) {
		fprintf(stderr, "[ptz][%s]: %s can't get ack\n", s->name, __FUNCTION__);
		return -1;
	}
	else if (rc) {
		print_err(rc);
		return -1000+rc;
	}

	// 不关心完成 :)

	return 0;

}

int visca_zoom_stop(visca_serial_t *s, int addr)
{
	// 8x 01 04 07 00 FF
	addr &= 0x7;
	unsigned char codes[6] = { 0x80 | addr, 1, 4, 7, 0, 0xff };
	int n = sizeof(codes)/sizeof(unsigned char);
	if (serial_write(s->serial, codes, n) != n) {
		fprintf(stderr, "[ptz][%s]: %s write comm err!\n", s->name, __FUNCTION__);
		return -1;
	}

	int who;
	int rc = get_next_ack(s, &who);
	if (rc < 0) {
		fprintf(stderr, "[ptz][%s]: %s can't get ack\n", s->name, __FUNCTION__);
		return -1;
	}
	else if (rc) {
		print_err(rc);
		return -1000+rc;
	}

	// 不关心完成 :)

	return 0;
}

int visca_set_zoom(visca_serial_t *s, int addr, int x, int wait)
{
	short xx = (short)x;
	unsigned char *px = (unsigned char*)&xx;

	// 8x 01 04 47 0Z 0Z 0Z 0Z FF
	addr &= 0x7;
	unsigned char codes[9] = { 0x80|addr, 1, 4, 0x47, 
		px[1]>>4, px[1]&0xf, px[0]>>4, px[0]&0xf, 
		0xff };
	int n = sizeof(codes);
	if (serial_write(s->serial, codes, n) != n) {
		fprintf(stderr, "[ptz][%s]: %s write comm err!\n", s->name, __FUNCTION__);
		return -1;
	}

	int who;
	int rc = get_next_ack(s, &who);
	if (rc < 0) {
		fprintf(stderr, "[ptz][%s]: %s can't get ack\n", s->name, __FUNCTION__);
		return -1;
	}
	else if (rc) {
		print_err(rc);
		return -1000 + rc;
	}

	if (wait) {
		rc = get_complete(s, &who);
		if (rc < 0) {
			fprintf(stderr, "[ptz][%s]: %s can't get completion packet\n", s->name, __FUNCTION__);
			return -1;
		}
		else if (rc) {
			print_err(rc);
			return -1000+rc;
		}
	}

	return 0;

}

int visca_get_zoom(visca_serial_t *s, int addr, int *x)
{
	// 8x 09 04 47 FF
	addr &= 0x07;
	unsigned char codes[5] = { 0x80|addr, 9, 4, 0x47, 0xff };
	int n = sizeof(codes);
	if (serial_write(s->serial, codes, n) != n) {
		fprintf(stderr, "[ptz][%s]: %s write comm err\n!", s->name, __FUNCTION__);
		return -1;
	}

	unsigned char res[16];
	int who;
	int rc = get_response(s, &who, res, sizeof(res));
	if (rc == 0) {
		short h = 0;
		unsigned char *ph = (unsigned char*)&h;
		ph[0] = res[4]<<4 | res[5];
		ph[1] = res[2]<<4 | res[3];

		*x = h;
		return 0;
	}
	else if (rc < 0) {
		fprintf(stderr, "[ptz][%s]: %s can't get response!\n", s->name, __FUNCTION__);
		return -1;
	}
	else {
		print_err(rc);
		return -1000+rc;
	}
}

int visca_preset_call(visca_serial_t *s, int addr, int id)
{
	// 8x 01 04 3F 02 0Z FF
	addr &= 0x7;
	unsigned char codes[7] = { 0x80|addr, 1, 4, 0x3f, 2, id, 0xff };
	int n = sizeof(codes)/sizeof(unsigned char);
	if (serial_write(s->serial, codes, n) != n) {
		fprintf(stderr, "[ptz][%s]: %s write comm err!\n", s->name, __FUNCTION__);
		return -1;
	}

	int who;
	int rc = get_next_ack(s, &who);
	if (rc < 0) {
		fprintf(stderr, "[ptz][%s]: %s can't get ack\n", s->name, __FUNCTION__);
		return -1;
	}
	else if (rc) {
		print_err(rc);
		return -1000+rc;
	}

	// 不关心完成 :)

	return 0;
}

int visca_preset_save(visca_serial_t *s, int addr, int id)
{
	// 8x 01 04 3F 01 0Z FF
	addr &= 0x7;
	unsigned char codes[7] = { 0x80|addr, 1, 4, 0x3f, 1, id, 0xff };
	int n = sizeof(codes)/sizeof(unsigned char);
	if (serial_write(s->serial, codes, n) != n) {
		fprintf(stderr, "[ptz][%s]: %s write comm err!\n", s->name, __FUNCTION__);
		return -1;
	}

	int who;
	int rc = get_next_ack(s, &who);
	if (rc < 0) {
		fprintf(stderr, "[ptz][%s]: %s can't get ack\n", s->name, __FUNCTION__);
		return -1;
	}
	else if (rc) {
		print_err(rc);
		return -1000+rc;
	}

	// 不关心完成 :)

	return 0;
}

int visca_preset_clear(visca_serial_t *s, int addr, int id)
{
	// 8x 01 04 3F 00 0Z FF
	addr &= 0x7;
	unsigned char codes[7] = { 0x80|addr, 1, 4, 0x3f, 0, id, 0xff };
	int n = sizeof(codes)/sizeof(unsigned char);
	if (serial_write(s->serial, codes, n) != n) {
		fprintf(stderr, "[ptz][%s]: %s write comm err!\n", s->name, __FUNCTION__);
		return -1;
	}

	int who;
	int rc = get_next_ack(s, &who);
	if (rc < 0) {
		fprintf(stderr, "[ptz][%s]: %s can't get ack\n", s->name, __FUNCTION__);
		return -1;
	}
	else if (rc) {
		print_err(rc);
		return -1000+rc;
	}

	// 不关心完成 :)

	return 0;
}

int visca_get_power(visca_serial_t *s, int addr, int *power)
{
	// 8x 09 04 00 FF
	// Y0 50 02 FF		ON
	// Y0 50 03 FF		OFF
	addr &= 0x7;
	unsigned char codes[5] = { 0x80|addr, 9, 4, 0, 0xff };
	int n = sizeof(codes);
	if (serial_write(s->serial, codes, n) != n) {
		fprintf(stderr, "[ptz][%s]: %s write comm err\n!", s->name, __FUNCTION__);
		return -1;
	}

	unsigned char res[16];
	int who;
	int rc = get_response(s, &who, res, sizeof(res));
	if (rc == 0) {
		if (res[2] == 2) {
			*power = 1;
		}
		else if (res[2] == 3) {
			*power = 0;
		}
		else {
			*power = 0;
			fprintf(stderr, "[ptz][%s]: %s !!!!!! power state=%d\n", res[2]);
		}
		return 0;
	}
	else if (rc < 0) {
		fprintf(stderr, "[ptz][%s]: %s can't get response!\n", s->name, __FUNCTION__);
		return -1;
	}
	else {
		print_err(rc);
		return -1000+rc;
	}

}
