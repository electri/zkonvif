#include <Windows.h>
#include "visca.h"
#include <map>
#include <string>
#include "SerialPort.h"
#include <assert.h>

typedef std::map<std::string, SerialPort*> PORTS;
static PORTS _ports;

typedef struct visca_t
{
	SerialPort *port;
	int addr;
	unsigned char err;	// 保存 z0 60 XX FF
	unsigned char ibuf[16];
	int data_len;
} visca_t;

visca_t *visca_open(const char *serial_name, int addr)
{
	// FIXME: 需要加锁 ..
	SerialPort *sp = 0;

	PORTS::iterator it = _ports.find(serial_name);
	if (it == _ports.end()) {
		sp = new SerialPort;
		if (sp->open(serial_name) < 0) {
			delete sp;
			sp = 0;
		}
		
		// 失败也保存，这样不必再次尝试了 ..
		_ports[serial_name] = sp;
	}
	else {
		sp = it->second;
	}

	if (!sp) {
		fprintf(stderr, "ERROR: %s: can't open %s:%d\n", __FUNCTION__, serial_name, addr);
		return 0;
	}

	visca_t *visca = new visca_t;
	visca->port = sp;
	visca->addr = addr;

	return visca;
}

void visca_close(visca_t *ctx)
{
	// FIXME: 没有考虑释放串口，等进程结束得了.
	delete ctx;
}

static void dump_hex(const unsigned char *data, int size)
{
	for (int i = 0; i < size; i++) {
		fprintf(stderr, "%02X ", data[i]);
	}
	fprintf(stderr, "\n");
}

/** 得到一个 visca package，成功返收到的字节数目，小于0失败 */
static int get_package(SerialPort *sp, unsigned char buf[16])
{
	int n = 0;
	if (sp->read_byte(buf[0]) < 0) {
		return -1;
	}

	while (buf[n] != 0xff && n < 16) { // VISCA 包最大 16 字节.
		n++;
		if (sp->read_byte(buf[n]) < 0) {
			return -1;
		}
	}

	n++;
	if (n < 16) {
		//dump_hex(buf, n);
		return n;
	}
	else {
		fprintf(stderr, "ERROR: %s: toooo many bytes for VISCA ?????????\n", __FUNCTION__);
		exit(-1);
	}
}

/** 发送命令，并等待得 ACK 后返回，ACK 保存在 ibuf 中
 */
static int req_with_ack(visca_t *ctx, unsigned char *data, int len)
{
	if (ctx->port->write_bytes(data, len) < 0) {
		return -1;
	}

	bool got = false;
	ctx->err = 0;
	do {
		ctx->data_len = get_package(ctx->port, ctx->ibuf);
		if (ctx->data_len < 0) {
			return -1;
		}

		if (ctx->ibuf[1] == 0x60) {
			ctx->err = ctx->ibuf[2];
			return 0;
		}
		got = (ctx->ibuf[1] & 0x40) == 0x40;		// z0 4y ff
	} while (!got);

	return ctx->data_len;
}

/** 发送命令，等待收到完成命令后返回 */
static int req_with_completion(visca_t *ctx, unsigned char *data, int len)
{
	if (ctx->port->write_bytes(data, len) < 0) {
		return -1;
	}

	ctx->err = 0;
	bool got = false;
	do {
		ctx->data_len = get_package(ctx->port, ctx->ibuf);
		if (ctx->data_len < 0) {
			return -1;
		}

		if (ctx->ibuf[1] == 0x60) {
			ctx->err = ctx->ibuf[2];
			return 0;
		}

		// z0 5y ff，其中 y 为socket，或1 或2
		if (ctx->ibuf[1] == 0x51 || ctx->ibuf[1] == 0x52) {
			got = true;
		}

	} while (!got);	

	return ctx->data_len;
}

/** 发送命令，等待收到查询信息 */
static int req_with_inquire(visca_t *ctx, unsigned char *data, int len)
{
	if (ctx->port->write_bytes(data, len) < 0) {
		return -1;
	}

	bool got = false;
	ctx->err = 0;

	do {
		ctx->data_len = get_package(ctx->port, ctx->ibuf);
		if (ctx->data_len < 0) {
			return -1;
		}

		if (ctx->ibuf[1] == 0x60) {
			ctx->err = ctx->ibuf[2];
			return 0;
		}

		got = ctx->ibuf[1] == 0x50;	// z0 50 .... ff
	} while (!got);

	return ctx->data_len;
}

int visca_left(visca_t *ctx, int speed)
{
	// 8x 01 06 01 VV WW 01 03 FF
	unsigned char buf[16];
	
	buf[0] = 0x80 | ctx->addr;
	buf[1] = 0x01;
	buf[2] = 0x06;
	buf[3] = 0x01;
	buf[4] = speed;
	buf[5] = 0;
	buf[6] = 0x01;
	buf[7] = 0x03;
	buf[8] = 0xff;

	int rc = req_with_completion(ctx, buf, 9);
	if (rc < 0) {
		return rc;
	}

	// 检查 err
	if (ctx->err) {
		fprintf(stderr, "ERR: %s: ptz err of %02x\n", __FUNCTION__, ctx->err);
	}

	return ctx->err;
}

int visca_right(visca_t *ctx, int speed)
{
	// 8x 01 06 01 VV WW 02 03 FF
	unsigned char buf[16];

	buf[0] = 0x80 | ctx->addr;
	buf[1] = 0x01;
	buf[2] = 0x06;
	buf[3] = 0x01;
	buf[4] = speed;
	buf[5] = 0;
	buf[6] = 0x02;
	buf[7] = 0x03;
	buf[8] = 0xff;

	int rc = req_with_completion(ctx, buf, 9);
	if (rc < 0) {
		return rc;
	}

	// 检查 err
	if (ctx->err) {
		fprintf(stderr, "ERR: %s: ptz err of %02x\n", __FUNCTION__, ctx->err);
	}

	return ctx->err;
}

int visca_up(visca_t *ctx, int speed)
{
	// 8x 01 06 01 VV WW 03 01 FF
	unsigned char buf[16];

	buf[0] = 0x80 | ctx->addr;
	buf[1] = 0x01;
	buf[2] = 0x06;
	buf[3] = 0x01;
	buf[4] = 0;
	buf[5] = speed;
	buf[6] = 0x03;
	buf[7] = 0x01;
	buf[8] = 0xff;

	int rc = req_with_completion(ctx, buf, 9);
	if (rc < 0) {
		return rc;
	}

	// 检查 err
	if (ctx->err) {
		fprintf(stderr, "ERR: %s: ptz err of %02x\n", __FUNCTION__, ctx->err);
	}

	return ctx->err;
}

int visca_down(visca_t *ctx, int speed)
{
	// 8x 01 06 01 VV WW 03 02 FF
	unsigned char buf[16];

	buf[0] = 0x80 | ctx->addr;
	buf[1] = 0x01;
	buf[2] = 0x06;
	buf[3] = 0x01;
	buf[4] = 0;
	buf[5] = speed;
	buf[6] = 0x03;
	buf[7] = 0x02;
	buf[8] = 0xff;

	int rc = req_with_completion(ctx, buf, 9);
	if (rc < 0) {
		return rc;
	}

	// 检查 err
	if (ctx->err) {
		fprintf(stderr, "ERR: %s: ptz err of %02x\n", __FUNCTION__, ctx->err);
	}

	return ctx->err;
}

int visca_stop(visca_t *ctx)
{
	// 8x 01 06 01 VV WW 03 03 FF
	unsigned char buf[16];

	buf[0] = 0x80 | ctx->addr;
	buf[1] = 0x01;
	buf[2] = 0x06;
	buf[3] = 0x01;
	buf[4] = 0;
	buf[5] = 0;
	buf[6] = 0x03;
	buf[7] = 0x03;
	buf[8] = 0xff;

	int rc = req_with_completion(ctx, buf, 9);
	if (rc < 0) {
		return rc;
	}

	// 检查 err
	if (ctx->err) {
		fprintf(stderr, "ERR: %s: ptz err of %02x\n", __FUNCTION__, ctx->err);
	}

	return ctx->err;
}

int visca_setpos(visca_t *ctx, short x, short y, int sx, int sy)
{

	// 8x 01 06 02 VV WW 0Y 0Y 0Y 0Y 0Z 0Z 0Z 0Z FF
	unsigned char buf[16];

	if (sx > 0x18) sx = 0x18;
	if (sx < 1) sx = 1;
	if (sy > 0x14) sy = 0x14;
	if (sy < 1) sy = 1;

	buf[0] = 0x80 | ctx->addr;
	buf[1] = 0x01;
	buf[2] = 0x06;
	buf[3] = 0x02;
	buf[4] = sx;
	buf[5] = sy;
	buf[6] = (x & 0xf000) >> 12;
	buf[7] = (x & 0x0f00) >> 8;
	buf[8] = (x & 0x00f0) >> 4;
	buf[9] = (x & 0x000f);
	buf[10] = (y & 0xf000) >> 12;
	buf[11] = (y & 0x0f00) >> 8;
	buf[12] = (y & 0x00f0) >> 4;
	buf[13] = (y & 0x000f);
	buf[14] = 0xff;

	int rc = req_with_ack(ctx, buf, 15);
	if (rc < 0) {
		return rc;
	}

	// 检查 err
	if (ctx->err) {
		fprintf(stderr, "ERR: %s: ptz err of %02x\n", __FUNCTION__, ctx->err);
	}

	return ctx->err;
}

int visca_setpos_blocked(visca_t *ctx, short x, short y, int sx, int sy)
{
	// 8x 01 06 02 VV WW 0Y 0Y 0Y 0Y 0Z 0Z 0Z 0Z FF
	unsigned char buf[16];

	if (sx > 0x18) sx = 0x18;
	if (sx < 1) sx = 1;
	if (sy > 0x14) sy = 0x14;
	if (sy < 1) sy = 1;

	buf[0] = 0x80 | ctx->addr;
	buf[1] = 0x01;
	buf[2] = 0x06;
	buf[3] = 0x02;
	buf[4] = sx;
	buf[5] = sy;
	buf[6] = (x & 0xf000) >> 12;
	buf[7] = (x & 0x0f00) >> 8;
	buf[8] = (x & 0x00f0) >> 4;
	buf[9] = (x & 0x000f);
	buf[10] = (y & 0xf000) >> 12;
	buf[11] = (y & 0x0f00) >> 8;
	buf[12] = (y & 0x00f0) >> 4;
	buf[13] = (y & 0x000f);
	buf[14] = 0xff;

	int rc = req_with_completion(ctx, buf, 15);
	if (rc < 0) {
		return rc;
	}

	// 检查 err
	if (ctx->err) {
		fprintf(stderr, "ERR: %s: ptz err of %02x\n", __FUNCTION__, ctx->err);
	}

	return ctx->err;
}

int visca_getpos(visca_t *ctx, short *x, short *y)
{
	// 8x 09 06 12 FF
	// Y0 50 0W 0W 0W 0W 0Z 0Z 0Z 0Z FF
	unsigned char buf[16];

	buf[0] = 0x80 | ctx->addr;
	buf[1] = 0x09;
	buf[2] = 0x06;
	buf[3] = 0x12;
	buf[4] = 0xff;

	int rc = req_with_inquire(ctx, buf, 5);
	if (rc < 0) {
		return rc;
	}

	if (ctx->err) {
		fprintf(stderr, "ERR: %s: ptz err of %02x\n", __FUNCTION__, ctx->err);
		return ctx->err;
	}

	assert(ctx->data_len == 11);
	assert(((ctx->ibuf[0] & 0xf0) >> 4) - 8 == ctx->addr);

	unsigned char *px = (unsigned char*)x, *py = (unsigned char*)y;
	px[1] = ctx->ibuf[2] << 4 | ctx->ibuf[3];
	px[0] = ctx->ibuf[4] << 4 | ctx->ibuf[5];
	py[1] = ctx->ibuf[6] << 4 | ctx->ibuf[7];
	py[0] = ctx->ibuf[8] << 4 | ctx->ibuf[9];

	return 0;
}

int visca_zoom_set(visca_t *ctx, int z)
{
	// 8x 01 04 47 0Z 0Z 0Z 0Z FF
	unsigned char buf[16];

	buf[0] = 0x80 | ctx->addr;
	buf[1] = 0x01;
	buf[2] = 0x04;
	buf[3] = 0x47;
	buf[4] = (z & 0xf000) >> 12;
	buf[5] = (z & 0x0f00) >> 8;
	buf[6] = (z & 0x00f0) >> 4;
	buf[7] = (z & 0x000f) >> 0;
	buf[8] = 0xff;

	int rc = req_with_ack(ctx, buf, 9);
	if (rc < 0) {
		return rc;
	}

	// 检查 err
	if (ctx->err) {
		fprintf(stderr, "ERR: %s: ptz err of %02x\n", __FUNCTION__, ctx->err);
	}

	return ctx->err;
}

int visca_zoom_set_blocked(visca_t *ctx, int z)
{
	// 8x 01 04 47 0Z 0Z 0Z 0Z FF
	unsigned char buf[16];

	if (z < 0) z = 0;

	buf[0] = 0x80 | ctx->addr;
	buf[1] = 0x01;
	buf[2] = 0x04;
	buf[3] = 0x47;
	buf[4] = (z & 0xf000) >> 12;
	buf[5] = (z & 0x0f00) >> 8;
	buf[6] = (z & 0x00f0) >> 4;
	buf[7] = (z & 0x000f) >> 0;
	buf[8] = 0xff;

	int rc = req_with_completion(ctx, buf, 9);
	if (rc < 0) {
		return rc;
	}

	// 检查 err
	if (ctx->err) {
		fprintf(stderr, "ERR: %s: ptz err of %02x\n", __FUNCTION__, ctx->err);
	}

	return ctx->err;
}

int visca_zoom_get(visca_t *ctx, int *z)
{
	// 8x 09 04 47 FF 
	// Y0 50 0Z 0Z 0Z 0Z FF
	unsigned char buf[16];

	buf[0] = 0x80 | ctx->addr;
	buf[1] = 0x09;
	buf[2] = 0x04;
	buf[3] = 0x47;
	buf[4] = 0xff;

	int rc = req_with_inquire(ctx, buf, 5);
	if (rc < 0) {
		return rc;
	}

	if (ctx->err) {
		fprintf(stderr, "ERR: %s: ptz err of %02x\n", __FUNCTION__, ctx->err);
		return ctx->err;
	}

	short zoom;
	unsigned char *pz = (unsigned char*)&zoom;
	pz[1] = ctx->ibuf[2] << 4 | ctx->ibuf[3];
	pz[0] = ctx->ibuf[4] << 4 | ctx->ibuf[5];

	*z = zoom;
	return 0;
}

int visca_get_max_speed(visca_t *ctx, int *sx, int *sy)
{
	// 8x 09 06 11 FF 
	// Y0 50 WW ZZ FF
	unsigned char buf[16];

	buf[0] = 0x80 | ctx->addr;
	buf[1] = 0x09;
	buf[2] = 0x06;
	buf[3] = 0x11;
	buf[4] = 0xff;

	int rc = req_with_inquire(ctx, buf, 5);
	if (rc < 0) {
		return rc;
	}

	*sx = ctx->ibuf[2], *sy = ctx->ibuf[3];

	return 0;
}
