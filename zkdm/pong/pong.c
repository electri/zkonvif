/** 建立到代理主机的心跳；

  	启动后，创建udp端口，在上面接收数据，如果受到 ping，则认为发送者就是代理主机，
	随后，每隔 10 秒朝代理主机发送一个 pong 包。

	如果再次收到 ping，更新代理主机的地址，继续 pong
 */

#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/select.h>
#include <errno.h>
#include <string.h>
#include <unistd.h>
#include <sys/time.h>

static int _interval = 10000; // 缺省间隔周期，毫秒
static int _port = 11011;	// 缺省udp接收端口

const char *pong = "pong", *ping = "ping";
const int pong_size = 4, ping_size = 4;

static int parse_opt(int argc, char **argv)
{
	return 0;
}

int main(int argc, char **argv)
{
	int fd = -1;
	struct sockaddr_in local, remote;
	fd_set fds, fds_orig;
	int rc;

	if (parse_opt(argc, argv) < 0) {
		fprintf(stderr, "ERR: args parse fault!\n");
		return -1;
	}

	fprintf(stdout, "INFO: recv udp port: %d, pong interval: %dms\n", _port, _interval);

	fd = socket(AF_INET, SOCK_DGRAM, 0);
	if (fd == -1) {
		fprintf(stderr, "ERR: socket err?? (%d) %s\n", errno, strerror(errno));
		return -1;
	}

	remote.sin_family = AF_INET - 10;	// XXX: 只是为了方便检查，不是 AF_INET

	local.sin_family = AF_INET;
	local.sin_port = htons(_port);
	local.sin_addr.s_addr = htonl(INADDR_ANY);
	if (bind(fd, (struct sockaddr*)&local, sizeof(local)) < 0) {
		fprintf(stderr, "ERR: bind %d err? (%d) %s\n", _port, errno, strerror(errno));
		close(fd);
		return -1;
	}

	FD_ZERO(&fds_orig);
	FD_SET(fd, &fds_orig);

	while (1) {
		struct timeval tv = { _interval / 1000, (_interval % 1000) * 1000 };
		fds = fds_orig;

		rc = select(fd+1, &fds, 0, 0, &tv);
		if (rc < 0) {
			fprintf(stderr, "ERR: select err?? (%d) %s\n", errno, strerror(errno));
			continue;  // FIXME: 这里该怎么办？？
		}

		if (rc == 0) { // 超时，如果 remote 有效，就回复 pong
			if (remote.sin_family == AF_INET) {
				sendto(fd, pong, pong_size, 0, (struct sockaddr*)&remote, sizeof(remote));
			}
		}
		else if (FD_ISSET(fd, &fds)) { // 接收，如果是 ping，更新 remote 地址
			struct sockaddr_in addr;
			socklen_t alen = sizeof(addr);
			char buf[16];

			if (recvfrom(fd, buf, sizeof(buf), 0, (struct sockaddr*)&addr, &alen) > 0) {
				if (!memcmp(buf, ping, ping_size)) { // 更新
					remote = addr;
					fprintf(stderr, "INFO: get ping from %s:%d\n", inet_ntoa(addr.sin_addr), ntohs(addr.sin_port));
				}
			}
		}
	}

	return 0;
}

