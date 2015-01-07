/** 建立到代理主机的心跳, 通过组播方式，将自己的信息声明给代理服务器

  	启动后，创建udp端口，在上面接收数据，如果受到 ping，则认为发送者就是代理主机，
	随后，每隔 10 秒朝代理主机发送一个 pong 包。

	如果再次收到 ping，更新代理主机的地址，继续 pong

	如果连续长时间（3分钟）没有收到 ping，则停止发送 pong

	收到 ping 之前，每隔 10 秒，组播一次

	组播的内容，通过管道获取
		echo -ne "xxxxxx" > ./pong

	  或者指定文件：
		./pong -f info
 */

#include <stdio.h>
#include <stdlib.h>
#ifdef WIN32
#	include <winsock2.h>
#	include <time.h>
	typedef int socklen_t;
#	define __func__ __FUNCTION__
#	define snprintf _snprintf
#else
#	include <sys/types.h>
#	include <sys/socket.h>
#	include <arpa/inet.h>
#	include <netinet/in.h>
#	include <sys/select.h>
#	include <errno.h>
#	include <string.h>
#	include <unistd.h>
#	include <fcntl.h>
#	include <sys/time.h>
	typedef int SOCKET;
#endif 

#include "commdef.h"

static int _interval = 3; // 缺省间隔周期，秒.
static int _port = PP_PORT;	// 缺省udp接收端口.
static int _ping_interval = 60;	// 代理主机给 online 发送 ping 的时间间隔，秒.
static int _ping_wait_cnt = 3;  // 当连续 3 * _ping_interval 收不到 ping.
								// 则认为代理主机已经关闭，停止 pong
static time_t _last_ping_stamp = 0; // 最后收到 ping 的时间.

const char *pong = "pong", *ping = "ping";
const int pong_size = 4, ping_size = 4;

// stdin 有可能阻塞 fgets 的，所以使用 select 首先进行判断
// FIXME: windows 实现版本有问题!!!!!
static int can_read(int fd)
{
#ifdef WIN32
	int rc = 0;
	HANDLE h = GetStdHandle(STD_INPUT_HANDLE);
	if (WaitForSingleObject(h, 500) == WAIT_OBJECT_0) {
		rc = 1;
	}
	CloseHandle(h);
	return rc;
#else
	fd_set rds;
	struct timeval tv = { 0, 0 };

	FD_ZERO(&rds);
	FD_SET(fd, &rds);

	return select(fd+1, &rds, 0, 0, &tv) == 1;
#endif
}

// 从 fd 中读取所有数据，保存到 &info 中，需要分配内存 ...
static void load_info(FILE *fd, char **info)
{
	char line[128];
	while (fgets(line, sizeof(line), fd)) {
		int n = strlen(*info);
		*info = (char*)realloc(*info, n + strlen(line) + 1);
		strcpy((*info) + n, line);
	}
}

static int parse_opt(int argc, char **argv, char **info)
{
	int arg = 1;

	// TODO: 应该解析，不过使用环境变量更简单 :)
	char *p = getenv("pong_port");
	if (p) _port = atoi(p);

	p = getenv("pong_interval");
	if (p) _interval = atoi(p);

	p = getenv("ping_interval");
	if (p) _ping_interval = atoi(p);

	p = getenv("ping_wait_cnt");
	if (p) _ping_wait_cnt = atoi(p);

	while (arg < argc) {
		if (argv[arg][0] == '-') {
			switch (argv[arg][1]) {
			case 'f':
				if (arg+1 < argc) {
					FILE *fp = fopen(argv[arg+1], "r");
					if (!fp) {
						fprintf(stderr, "ERR: %s: -f <fname>\n", __FUNCTION__);
						return -1;
					}
					else {
						load_info(fp, info);
						fclose(fp);
					}

					arg++;
				}
				break;

			// case ...
			}
		}

		arg++;
	}

	return 0;
}

/** 将dat内容组播 */
static int multcast_info(SOCKET fd, const void *dat, size_t len)
{
	struct sockaddr_in maddr;
	
	maddr.sin_family = AF_INET;
	maddr.sin_port = htons(PP_MULTCAST_PORT);
	maddr.sin_addr.s_addr = inet_addr(PP_MULTCAST_ADDR);

	fprintf(stderr, "DEBUG: %s: send %s, len=%u\n", __func__, dat, len);

	return sendto(fd, (const char*)dat, len, 0, (struct sockaddr*)&maddr, sizeof(maddr));
}

int main(int argc, char **argv)
{
	SOCKET fd = -1;
	struct sockaddr_in local, remote;
	fd_set fds, fds_orig;
	int rc;
	time_t last_mc, now;
	const char *ip, *mac;
	char *info = strdup("pong\n"); // 为了方便过滤

	if (parse_opt(argc, argv, &info) < 0) {
		fprintf(stderr, "ERR: args parse fault!\n");
		return -1;
	}

#ifdef WIN32
#else
	if (strlen(info) == 5 && can_read(0)) { // info="pong\n", stdin = 0
		load_info(stdin, &info);	// echo "xxxxx" | ./pong
	}
#endif

	fprintf(stderr, "INFO: info=%s\n", info);

	fprintf(stdout, "INFO: recv udp port: %d, pong interval: %d seconds\n", 
			_port, _interval);

#ifdef WIN32
	do {
		WSADATA data;
		WSAStartup(0x202, &data);
	} while (0);
#endif

	fd = socket(AF_INET, SOCK_DGRAM, 0);
	if (fd == -1) {
		fprintf(stderr, "ERR: socket err?? (%d) %s\n", errno, strerror(errno));
		return -1;
	}
	else {  // non block io
#ifdef WIN32
		ULONG mode = 1;
		ioctlsocket(fd, FIONBIO, &mode);
#else
		int f = fcntl(fd, F_GETFL);
		fcntl(fd, F_SETFL, f | O_NONBLOCK);
#endif
	}

	remote.sin_family = AF_INET - 10;	// XXX: 只是为了方便检查，不是 AF_INET

	local.sin_family = AF_INET;
	local.sin_port = htons(_port);
	local.sin_addr.s_addr = htonl(INADDR_ANY);
	if (bind(fd, (struct sockaddr*)&local, sizeof(local)) < 0) {
		fprintf(stderr, "ERR: bind %d err? (%d) %s\n", _port, errno, strerror(errno));
		return -1;
	}

	FD_ZERO(&fds_orig);
	FD_SET(fd, &fds_orig);

	multcast_info(fd, info, strlen(info)+1);	// 首先发送组播信息
	last_mc = time(0);

	while (1) {
		struct timeval tv = { _interval, 0 };
		fds = fds_orig;
		rc = select(fd+1, &fds, 0, 0, &tv);
		if (rc < 0) {
			fprintf(stderr, "ERR: select err?? (%d) %s\n", errno, strerror(errno));
			continue;  // FIXME: 这里该怎么办?
		}

		if (rc == 0) { // 超时，如果 remote 有效，就回复 pong
			if (remote.sin_family == AF_INET) {
				if (time(0) - _last_ping_stamp > _ping_interval * _ping_wait_cnt) {
					// 长时间没有收到 ping，此时停止发送 pong
					remote.sin_family = AF_INET - 10;
					fprintf(stderr, "WARNING: can't get ping in %d seconds, stop pong\n",
							_ping_interval * _ping_wait_cnt);
				}
				else {
					sendto(fd, pong, pong_size, 0, (struct sockaddr*)&remote, sizeof(remote));
				}
			}
		}
		else if (FD_ISSET(fd, &fds)) { // 接收，如果是 ping，更新 remote 地址.
			struct sockaddr_in addr;
			socklen_t alen = sizeof(addr);
			char buf[16];

			if (recvfrom(fd, buf, sizeof(buf), 0, (struct sockaddr*)&addr, &alen) > 0) {
				if (!memcmp(buf, ping, ping_size)) { // 更新.
					remote = addr;
					_last_ping_stamp = time(0);
					fprintf(stderr, "INFO: get ping from %s:%d\n", inet_ntoa(addr.sin_addr), ntohs(addr.sin_port));
				}
			}
		}


		// 收到 ping 之前，每隔10秒, 发送组播信息.
		if (remote.sin_family != AF_INET) {
			now = time(0);
			if (now - last_mc > 10) {
				multcast_info(fd, info, strlen(info)+1); // 包含字符串结束符.
				last_mc = now;
			}
		}
	}

	return 0;
}

