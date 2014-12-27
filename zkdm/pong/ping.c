/** 建立到被代理主机们之间的联系：
  	如果没有收到被代理主机的 pong，则持续发送 ping
 */
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/select.h>
#include <sys/time.h>
#include <fcntl.h>
#include <string.h>
#include <errno.h>

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
} Target;

static Target _target_hosts = { 0 };	// 用于保存所有被代理主机的信息

static int parse_args(int argc, char **argv)
{
	_verbose = 1;
	return 0;
}

// 加载被代理主机的信息
static int load_target_hosts()
{
	// a test target
	Target *t = (Target*)malloc(sizeof(Target));
	t->next = 0;
	t->remote.sin_family = AF_INET;
	t->remote.sin_port = htons(11011);
	t->remote.sin_addr.s_addr = inet_addr("127.0.0.1");
	t->online = 0;
	
	_target_hosts.next = t;

	return 0;
}

// 对 _target_hosts 中所有 ! online 的发送 ping 消息
static int send_pings(int fd)
{
	const Target *target = _target_hosts.next;
	while (target) {
		if (!target->online) {
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

int main(int argc, char **argv)
{
	int fd = -1;
	fd_set fds, fds_saved;
	int rc;

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

	FD_ZERO(&fds_saved);
	FD_SET(fd, &fds_saved);

	// 作为发起者，无须主动绑定端口
	
	while (1) {
		struct timeval tv = { _interval, 0 }; // 
		fds = fds_saved;
		rc = select(fd+1, &fds, 0, 0, &tv);
		if (rc == -1) {
			fprintf(stderr, "ERR: select err?? (%d) %s\n", errno, strerror(errno));
			continue;	// FIXME: 应该如何处理呢
		}
		
		if (rc == 0) { // 超时
			send_pings(fd);
			check_timeout();
		}
		else if (FD_ISSET(fd, &fds)) {
			struct sockaddr_in remote;
			socklen_t len = sizeof(remote);
			char buf[16];
			rc = recvfrom(fd, buf, sizeof(buf), 0, (struct sockaddr*)&remote, &len);
			if (rc == pong_len && !memcmp(pong, buf, pong_len)) {
				update_pong(remote.sin_port, remote.sin_addr);
			}
		}
	}

	return 0;
}

