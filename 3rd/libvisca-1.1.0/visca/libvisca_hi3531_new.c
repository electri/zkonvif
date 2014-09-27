/* 为 hi3531 实现 ...
 */

#include "libvisca.h"
#include <stdio.h>
#include <stdlib.h>
#include <poll.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <fcntl.h>
#include <sys/select.h>

/* implemented in libvisca.c
 */
void _VISCA_append_byte(VISCAPacket_t *packet, unsigned char byte);
void _VISCA_init_packet(VISCAPacket_t *packet);
unsigned int _VISCA_get_reply(VISCAInterface_t *iface, VISCACamera_t *camera);
unsigned int _VISCA_send_packet_with_reply(VISCAInterface_t *iface, 
		VISCACamera_t *camera, VISCAPacket_t *packet);

/* Implementation of the platform specific code. The following functions must
 * be implemented here:
 *
 * unsigned int _VISCA_write_packet_data(VISCAInterface_t *iface, VISCACamera_t *camera, VISCAPacket_t *packet);
 * unsigned int _VISCA_send_packet(VISCAInterface_t *iface, VISCACamera_t *camera, VISCAPacket_t *packet);
 * unsigned int _VISCA_get_packet(VISCAInterface_t *iface);
 * unsigned int VISCA_open_serial(VISCAInterface_t *iface, const char *device_name);
 * unsigned int VISCA_close_serial(VISCAInterface_t *iface);
 * 
 */

typedef struct vk3344_inf_s
{	
    unsigned int id;	
    unsigned int baud;
} vk3344_inf;

#define VK3344_IOC_MAGIC       'v'
#define VK3344_GET_BAUD         _IOWR (VK3344_IOC_MAGIC, 1, vk3344_inf)
#define VK3344_SET_BAUD         _IOW (VK3344_IOC_MAGIC, 2, vk3344_inf)

static int set_speed(int dev_num, int fd, int speed)
{
    vk3344_inf inf;
    inf.id = dev_num;	
    ioctl(fd, VK3344_GET_BAUD, &inf);	
	fprintf(stderr, "dev_num=%d, baud=%d\n", dev_num, inf.baud);
    inf.id = dev_num;	
    inf.baud = speed;
    ioctl(fd, VK3344_SET_BAUD, &inf);
    sleep(1);
    return 0;
}

static int _poll(VISCAInterface_t *i, int timeout)
{
	int rc;
#if 1
	struct pollfd fds;
	fds.fd = i->port_fd;
	fds.events = POLLIN | POLLERR;
	rc = poll(&fds, 1, timeout);
	if (rc == 0)
		return 0;	// 超时 ..
	else if (rc == -1)
		return -1;	// 错误 ..
	else if (fds.revents & POLLIN)
		return 1;	// 有数据 ..
	else
		return -2;	// POLLERR ??
#else
	fd_set r;
	struct timeval tv;
	FD_ZERO(&r);
	FD_SET(i->port_fd, &r);

	tv.tv_sec = timeout / 1000;
	tv.tv_usec = (timeout % 1000) * 1000;

	rc = select(i->port_fd+1, &r, 0, 0, &tv);
	return rc;
#endif
}

static void dump(int out, const unsigned char *buf, int len)
{
	int i;
	if (out)
		fprintf(stderr, "========= SENT =========\n");
	else
		fprintf(stderr, "========= RECV =========\n");

	for (i = 0; i < len; i++)
		fprintf(stderr, "%02X ", buf[i]);

	fprintf(stderr, "\n----------------------\n");
}

/** 总是首先清空缓冲 */
static void _flush(VISCAInterface_t *i)
{
	/** FIXME: 
	  	只要 poll 有数据，recv 一次，就清空了 :(
	 */
	fprintf(stderr, " //// before flush ....");
	if (_poll(i, 0) > 0) {
		char c;
		read(i->port_fd, &c, 1);
	}
	fprintf(stderr, " end!\n");
}

uint32_t
_VISCA_write_packet_data(VISCAInterface_t * iface, VISCACamera_t * camera,
			 VISCAPacket_t * packet)
{
	int err;

	_flush(iface); // 发送命令之前，总是首先清空接收缓冲 ...

	dump(1, packet->bytes, packet->length);

	err = write(iface->port_fd, packet->bytes, packet->length);
	if (err < packet->length)
		return VISCA_FAILURE;
	else
		return VISCA_SUCCESS;
}

uint32_t
_VISCA_send_packet(VISCAInterface_t * iface, VISCACamera_t * camera,
		   VISCAPacket_t * packet)
{
	// check data:
	if ((iface->address > 7) || (camera->address > 7) || (iface->broadcast > 1)) {
		fprintf(stderr, "(%s): Invalid header parameters\n", __FILE__);
		fprintf(stderr, " %d %d %d   \n", iface->address, camera->address, iface->broadcast);
		return VISCA_FAILURE;
	}

	// build header:
	packet->bytes[0] = 0x80;
	packet->bytes[0] |= (iface->address << 4);

	if (iface->broadcast > 0) {
		packet->bytes[0] |= (iface->broadcast << 3);
		packet->bytes[0] &= 0xF8;
	} else
		packet->bytes[0] |= camera->address;

	// append footer
	_VISCA_append_byte(packet, VISCA_TERMINATOR);

	return _VISCA_write_packet_data(iface, camera, packet);
}

void _temination_get_packet(VISCAInterface_t *iface, int list_len, int &lpos)
{
	for (int i = 0; i < list_len; i++) {
		char ch;
		circque_front(&iface->list, &ch);
		circque_pop(&iface->list);
		*(iface->ibuf + *pos) = ch; // xxx:fixme ...
		iface->bytes = *pos + 1;
		if (ch == 0xFF) {
			return VISCA_SUCCESS;
		}
		if (iface->bytes > VISCA_INPUT_BUFFER_SIZE) {
			return VISCA_FAILURE;
		}
		(*pos)++;
	}
}

uint32_t _VISCA_get_packet(VISCAInterface_t * iface)
{
	int pos = 0;
	int bytes_read;
	unsigned char temp[VISCA_INPUT_BUFFER_SIZE];
	int list_len = 0;
	// 300ms 超时
	if (_poll(iface, 300) == 0) {
		fprintf(stderr, "WARNING: %s: timeout\n", __func__);
		return VISCA_FAILURE;
	}

	// 对于驱动vk3344，要求必须一次都读出来 :( 
	//bytes_read = read(iface->port_fd, iface->ibuf, VISCA_INPUT_BUFFER_SIZE);
	list_len = circque_get_len(&iface->ifac->list);
	if (list_len > 0) {
		 _temination_get_packet(VISCAInterface_t *iface, list_len, &pos);
	}
	else {
		while(list_len == 0) {
			bytes_read = read(iface->port_fd, temp, VISCA_INPUT_BUFFER_SIZE);
			if (bytes_read <= 0) {
				return VISCA_FAILURE;
			}

			for (int i = 0; i < bytes_read; i++) {
				circque_push(&iface->list, *(temp + i));
			}
		
			list_len = circque_get_len(&iface->list);
			 _temination_get_packet(VISCAInterface_t *iface, list_len, &pos);
			list_len = circque_get_len(&iface->list);
		}
	}
}		

/***********************************/
/*       SYSTEM  FUNCTIONS         */
/***********************************/
/**
  	device_name 总是 /dev/vktty.%d
 */
uint32_t VISCA_open_serial(VISCAInterface_t * iface, const char *device_name)
{
	int fd;
	int dev_num;

	if (sscanf(device_name, "%*[^.] . %d", &dev_num) != 1) {
		fprintf(stderr, "ERR: %s: device_name format MUST be /dev/vktty.%%d\n", __func__);
		iface->port_fd = -1;
		return VISCA_FAILURE;
	}

	fd = open(device_name, O_RDWR);

	if (fd == -1) {
		fprintf(stderr, "(%s): cannot open serial device %s\n",
			__FILE__, device_name);
		iface->port_fd = -1;
		return VISCA_FAILURE;
	} else {
		set_speed(dev_num, fd, 9600);
		fprintf(stderr, "DEBUG: %s: open '%s' ok\n", __func__, device_name);
	}

	iface->port_fd = fd;
	iface->address = 0;
	iface->want_result = 0;
	iface->temp_len = 0;

	circque_init(&iface->list);

	return VISCA_SUCCESS;
}

uint32_t
VISCA_unread_bytes(VISCAInterface_t * iface, unsigned char *buffer,
		   uint32_t * buffer_size)
{
	uint32_t bytes = 0;
	*buffer_size = 0;

	if (_poll(iface, 300) > 0) {	
		bytes = read(iface->port_fd, buffer, 30);
		if (bytes > 0) {
			*buffer_size = bytes;
			return VISCA_SUCCESS;
		} else 
			return VISCA_FAILURE;
	}
	return VISCA_SUCCESS;
}

uint32_t VISCA_close_serial(VISCAInterface_t * iface)
{
	if (iface->port_fd != -1) {
		close(iface->port_fd);
		iface->port_fd = -1;
		return VISCA_SUCCESS;
	} else
		return VISCA_FAILURE;
}

int usleep(uint32_t l);

uint32_t VISCA_usleep(uint32_t useconds)
{
	return (uint32_t) usleep(useconds);
}

