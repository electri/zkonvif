#pragma once

#include <assert.h>
#include <cc++/socket.h>
#include <cc++/network.h>
#include <cc++/address.h>
#ifdef WIN32
#	include <IPHlpApi.h>
#endif

#ifndef WIN32
#ifdef	HAVE_IOCTL_H
#include <ioctl.h>
#else
#include <sys/ioctl.h>
#endif
# ifdef HAVE_SYS_SOCKIO_H
# include <sys/sockio.h>
# endif
#ifdef	HAVE_NET_IF_H
#include <net/if.h>
#endif
#endif

// 判断 mac 是否为虚拟机 mac
inline bool is_vm_mac(const char *mac)
{
	/**
	"00:05:69"; //vmware1
	"00:0C:29"; //vmware2
	"00:50:56"; //vmware3
	"00:1C:42"; //parallels1
	"00:03:FF"; //microsoft virtual pc
	"00:0F:4B"; //virtual iron 4
	"00:16:3E"; //red hat xen , oracle vm , xen source, novell xen
	"08:00:27"; //virtualbox
	*/
	static const char *_vm_macs[] = {
		"000569",
		"000c29",
		"005056",
		"001c42",
		"0003ff",
		"000f4b",
		"00163e",
		"080027",
		0,
	};

	if (!mac) return true;	// FIXME:

	const char *p = _vm_macs[0];
	int n = 0;
	while (p) {
		if (strstr(mac, p))
			return true;
		n++;
		p = _vm_macs[n];
	}

	return false;
}

// 将 byte[] 类型，转换为小写的 ascii 字符串
inline std::string conv_mac(unsigned char mac[], int len)
{
	std::string s;
	char *buf = (char *)alloca(len * 2 + 1);
	buf[0] = 0;
	for (int pos = 0; len > 0; len--) {
		pos += sprintf(buf + pos, "%02x", *mac);
		mac++;
	}
	s = buf;
	return s;
}

// 描述一个网卡配置
struct NetInf
{
	std::string macaddr;
	std::vector<std::string> ips;
};

/** 获取可用网卡配置，仅仅选择启动的 ipv4的，非虚拟机的，ethernet
*/
inline bool get_all_netinfs(std::vector<NetInf> &nis)
{
	nis.clear();
#ifdef WIN32
	ULONG len = 16 * 1024;
	IP_ADAPTER_ADDRESSES *adapter = (IP_ADAPTER_ADDRESSES*)malloc(len);

	// 仅仅 ipv4
	DWORD rc = GetAdaptersAddresses(AF_INET, 0, 0, adapter, &len);
	if (rc == ERROR_BUFFER_OVERFLOW) {
		adapter = (IP_ADAPTER_ADDRESSES*)realloc(adapter, len);
		rc = GetAdaptersAddresses(AF_INET, 0, 0, adapter, &len);
	}

	if (rc == 0) {
		IP_ADAPTER_ADDRESSES *p = adapter;
		while (p) {
			if ((p->IfType == IF_TYPE_ETHERNET_CSMACD || p->IfType == IF_TYPE_IEEE80211) &&
				(p->OperStatus == IfOperStatusUp)) {
				// 仅仅考虑 ethernet 或者 wifi，并且活动的
				// 不包括虚拟机的 mac
				std::string mac = conv_mac(p->PhysicalAddress, p->PhysicalAddressLength);
				if (!is_vm_mac(mac.c_str())) {
					NetInf ni;
					ni.macaddr = mac;

					IP_ADAPTER_UNICAST_ADDRESS *ip = p->FirstUnicastAddress;
					while (ip) {
						assert(ip->Address.lpSockaddr->sa_family == AF_INET);
						sockaddr_in *addr = (sockaddr_in*)ip->Address.lpSockaddr;
						ni.ips.push_back(inet_ntoa(addr->sin_addr));

						ip = ip->Next;
					}

					nis.push_back(ni);
				}
			}
			p = p->Next;
		}

		free(adapter);
	}

#else
	char buffer[8192];
	struct ifconf ifc;
	struct ifreq ifr;

	int fd = socket(AF_INET, SOCK_DGRAM, 0);
	if (fd == -1)
		return false;

	ifc.ifc_len = sizeof(buffer);
	ifc.ifc_buf = buffer;

	if (ioctl(fd, SIOCGIFCONF, &ifc) == -1)
		return false;

	int count = ifc.ifc_len / sizeof(ifreq);

	struct ifreq *req = ifc.ifc_req;
	struct ifreq *end = req + count;
	for (; req != end; ++req) {
		strcpy(ifr.ifr_name, req->ifr_name);
		ioctl(fd, SIOCGIFFLAGS, &ifr);
		if (ifr.ifr_flags & IFF_LOOPBACK)
			continue;	// lo

		sockaddr_in sin;
		sin.sin_addr = ((sockaddr_in&)req->ifr_addr).sin_addr;

		ioctl(fd, SIOCGIFHWADDR, &ifr);
		unsigned char mac_addr[6];
		memcpy(mac_addr, ifr.ifr_hwaddr.sa_data, 6);

		NetInf ni;
		ni.ips.push_back(inet_ntoa(sin.sin_addr));
		ni.macaddr = conv_mac(mac_addr, 6);

		nis.push_back(ni);
	}
	close(fd);

#endif
	return true;
}

inline const char *util_get_myip_real()
{
	char *p = getenv("zonekey_my_ip_real");
	if (p) return p;

	static std::string _ip;
	if (_ip.empty()) {
		std::vector<NetInf> nis;
		get_all_netinfs(nis);
		if (nis.size() > 0) {
			if (nis[0].ips.size() > 0) {
				_ip = nis[0].ips[0];
			}
		}
	}

	if (_ip.empty())
		_ip = "000.000.000.000";
	return _ip.c_str();
}

inline const char *util_get_myip()
{
	char *p = getenv("zonekey_my_ip");
	if (p) return p;

	static std::string _ip;
	if (_ip.empty()) {
		std::vector<NetInf> nis;
		get_all_netinfs(nis);
		if (nis.size() > 0) {
			if (nis[0].ips.size() > 0) {
				_ip = nis[0].ips[0];
			}
		}
	}

	if (_ip.empty())
		_ip = "000.000.000.000";
	return _ip.c_str();
}

inline const char *util_get_mymac()
{
	char *p = getenv("zonekey_my_mac");
	if (p) return p;

	static std::string _mac;
	if (_mac.empty()) {
		std::vector<NetInf> nis;
		get_all_netinfs(nis);
		if (nis.size() > 0) {
			_mac = nis[0].macaddr;
		}
	}

	if (_mac.empty())
		_mac = "000000000000";
	return _mac.c_str();
}

