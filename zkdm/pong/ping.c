/** 建立到被代理主机们之间的联系：
  	如果没有收到被代理主机的 pong，则持续发送 ping

	加入组播地址，接收来自未指定的被代理主机的信息
 */
#include <stdio.h>
#include <stdlib.h>
#ifdef WIN32
#	include <winsock2.h>
	typedef int socklen_t;
#else
#	include <sys/types.h>
#	include <sys/socket.h>
#	include <arpa/inet.h>
#	include <netinet/in.h>
#	include <sys/select.h>
#	include <sys/time.h>
#	include <fcntl.h>
#	include <string.h>
#	include <errno.h>
#endif

#include "commdef.h"

const char *ping = "ping", *pong = "pong";
int ping_len = 4, pong_len = 4;
static int _interval = 10;		// 发送 ping 的时间间隔，使用秒作单位足够了
static int _max_interval = 15; // 如果 last_updated 超过这个时间，则认为 target 已经 offline
							   // pong 缺省 3 秒发送一次 .
static int _verbose = 0;

typedef struct Target {
	struct Target *next;		// 指向下一个，最后一个为 0
	struct sockaddr_in remote;	// 目标主机 socket addr
	int online;		// 是否在线
	time_t last_updated;	// 最后收到 pong 的时间
	char *private;	// 来自 target 的私有描述，对应的，通过target发送组播包中的信息
} Target;

static Target _target_hosts = { 0 };	// 用于保存所有被代理主机的信息

static int parse_args(int argc, char **argv)
{
	_verbose = 1;
	return 0;
}

static void non_block(int fd)
{
#ifdef WIN32
	ULONG mode = 1;
	ioctlsocket(fd, FIONBIO, &mode);
#else
	int f = fcntl(fd, F_GETFL);
	fcntl(fd, F_SETFL, f | O_NONBLOCK);
#endif
}

// 加载被代理主机的信息
static int load_target_hosts()
{
	// a test target
	Target *t = (Target*)malloc(sizeof(Target)), *t2 = (Target*)malloc(sizeof(Target));
	t->next = 0;
	t->remote.sin_family = AF_INET;
	t->remote.sin_port = htons(PP_PORT);
	t->remote.sin_addr.s_addr = inet_addr("127.0.0.1");
	t->online = 0;
	t->private = strdup(""); // :)

	// a test target
	t2->next = t;
	t2->remote.sin_family = AF_INET;
	t2->remote.sin_port = htons(11010); // XXX: 故意模拟不存在的
	t2->remote.sin_addr.s_addr = inet_addr("127.0.0.1");
	t->online = 0;
	t->private = strdup(""); // :)
	
	_target_hosts.next = t2;

	return 0;
}

// 对 _target_hosts 中所有 ! online 的发送 ping 消息
static int send_pings(int fd)
{
	/** 每隔 1 分钟，给所有在线的 target 也发送 ping
	  	这样即使 ping 结束，target 也能停止发送 pong
	 */
	static time_t last_ping_for_online = 0;
	const Target *target = _target_hosts.next;
	int to_online = 0;
	time_t now = time(0);

	if (now - last_ping_for_online > 60) {
		to_online = 1;
		last_ping_for_online = now;
	}

	while (target) {
		if (!target->online || to_online) {
			if (_verbose) {
				fprintf(stderr, "INFO: sendto %s:%d\n", inet_ntoa(target->remote.sin_addr), 
						ntohs(target->remote.sin_port));
			}
			sendto(fd, ping, ping_len, 0, (struct sockaddr*)&target->remote, sizeof(target->remote));
		}
		
		target = target->next;
	}
	return 0;
}

// 检查 _target_hosts 中是否超时
static int check_timeout()
{
	Target *target = _target_hosts.next;
	time_t now = time(0);

	while (target) {
		if (target->online && now - target->last_updated > _max_interval) {
			if (_verbose) {
				fprintf(stderr, "WARNING: oh %s:%d TIMEOUT, to offline\n", 
						inet_ntoa(target->remote.sin_addr), ntohs(target->remote.sin_port));
			}
			target->online = 0;
		}
		target = target->next;
	}
	return 0;
}

// 更新 _target_hosts 中的 last_updated
static int update_pong(int port, struct in_addr addr)
{
	Target *target = _target_hosts.next;
	while (target) {
		if (target->remote.sin_port == port && target->remote.sin_addr.s_addr == addr.s_addr) {
			target->last_updated = time(0);
			if (_verbose) {
				fprintf(stderr, "INFO: update %s:%d\n", 
						inet_ntoa(target->remote.sin_addr), ntohs(target->remote.sin_port));
			}
			target->online = 1;
			break;
		}
		target = target->next;
	}
	return 0;
}

// 根据ip检查是否以及在target列表中了?
static Target *find_target(struct in_addr addr)
{
	Target *t = _target_hosts.next;
	uint32_t d = addr.s_addr;

	while (t) {
		if (d == t->remote.sin_addr.s_addr) {
			return t;
		}

		t = t->next;
	}

	return 0;
}

// 收到组播信息,更新初始列表
static int update_proxied(struct in_addr addr, const char *data)
{
	Target *t = find_target(addr);
	if (!t) {
		t = (Target*)malloc(sizeof(Target));
		t->remote.sin_family = AF_INET;
		t->remote.sin_port = htons(PP_PORT);
		t->remote.sin_addr = addr;
		t->online = 0;
		t->private = strdup(data);
		t->next = _target_hosts.next;
		_target_hosts.next = t;
	}

	return 0;
}

// 启动socket加入组播地址, 返回 socket 句柄
static int open_multcast_recver()
{
	int fd = -1;
	struct sockaddr_in local;
	struct ip_mreq group;

	fd = socket(AF_INET, SOCK_DGRAM, 0);
	if (fd == -1) {
		fprintf(stderr, "ERR: %s: open sock fault?\n", __FUNCTION__);
		return -1;
	}

	local.sin_family = AF_INET;
	local.sin_port = htons(PP_MULTCAST_PORT);
	local.sin_addr.s_addr = INADDR_ANY;

	if (bind(fd, (struct sockaddr*)&local, sizeof(local)) < 0) {
		fprintf(stderr, "ERR: %s: bind port %d fault\n", __FUNCTION__, PP_MULTCAST_PORT);
#ifdef WIN32
		closesocket(fd);
#else
		close(fd);
#endif
		return -1;
	}

	group.imr_multiaddr.s_addr = inet_addr(PP_MULTCAST_ADDR);
	group.imr_interface.s_addr = INADDR_ANY;

	if (setsockopt(fd, IPPROTO_IP, IP_ADD_MEMBERSHIP, (char*)&group, sizeof(group)) < 0) {
		fprintf(stderr, "ERR: %s: join %s fault!\n", __FUNCTION__, PP_MULTCAST_ADDR);
#ifdef WIN32
		closesocket(fd);
#else
		close(fd);
#endif
		return -1;
	}

	non_block(fd);

	return fd;
}

int main(int argc, char **argv)
{
	int fd = -1, mfd = -1, maxfd = -1;
	fd_set fds, fds_saved;
	time_t last;
	int rc;

#ifdef WIN32
	WSADATA data;
	WSAStartup(0x202, &data);
#endif

	if (parse_args(argc, argv) < 0) {
		fprintf(stderr, "ERR: args parse err\n");
		return -1;
	}

	if (load_target_hosts() < 0) {
		fprintf(stderr, "ERR: load target hosts info err\n");
		return -2;
	}

	fd = socket(AF_INET, SOCK_DGRAM, 0);
	if (fd == -1) {
		fprintf(stderr, "ERR: socket fault ?? (%d) %s\n", errno, strerror(errno));
		return -1;
	}

	non_block(fd);
	maxfd = fd;

	FD_ZERO(&fds_saved);
	FD_SET(fd, &fds_saved);

	mfd = open_multcast_recver();
	if (mfd != -1) {
		FD_SET(mfd, &fds_saved);

		if (mfd > maxfd) {
			maxfd = mfd;
		}
	}

	// 作为发起者，无须主动绑定端口

	last = time(0);
	
	while (1) {
		time_t curr = time(0);
		struct timeval tv = { _interval, 0 }; // 
		fds = fds_saved;
		rc = select(maxfd+1, &fds, 0, 0, &tv);
		if (rc == -1) {
			fprintf(stderr, "ERR: select err?? (%d) %s\n", errno, strerror(errno));
			continue;	// FIXME: 应该如何处理呢
		}
		
		if (rc == 0) { // 超时
			send_pings(fd);
			check_timeout();
			last = curr;
		}
		else {
			if (FD_ISSET(fd, &fds)) {
				struct sockaddr_in remote;
				socklen_t len = sizeof(remote);
				char buf[16];
				rc = recvfrom(fd, buf, sizeof(buf), 0, (struct sockaddr*)&remote, &len);
				if (rc == pong_len && !memcmp(pong, buf, pong_len)) {
					update_pong(remote.sin_port, remote.sin_addr);
				}
			}

			if (FD_ISSET(mfd, &fds)) {
				// 收到组播消息, "ip mac" 格式, 更新到被代理主机信息表中 :(
				struct sockaddr_in remote;
				socklen_t len = sizeof(remote);
				char buf[65536];  // 
				rc = recvfrom(mfd, buf, sizeof(buf), 0, (struct sockaddr*)&remote, &len);
				if (rc > 5 && strncmp(buf, "pong\n", 5) == 0) {
					update_proxied(remote.sin_addr, buf+5);
				}
			}

			/** XXX: 因为同时处理多路target，有可能频繁进入 FD_ISSET 而无超时，导致无法发出
			  ping 和检查超时了，所以这里应进行处理
			 */
			if (curr - last >= _interval) {
				send_pings(fd);
				check_timeout();
				last = curr;
			}

		}
	}

	return 0;
}

