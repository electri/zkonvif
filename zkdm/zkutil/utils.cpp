
#include <stdio.h>
#include <stdlib.h>

#ifdef WIN32
#	include <winsock2.h>
#	include <iphlpapi.h>
#	include <comutil.h>
#	pragma comment(lib, "comsuppw.lib")
#	pragma comment(lib, "iphlpapi.lib")
#	pragma comment(lib, "ws2_32.lib")
#else
#	include <unistd.h>
#	include <sys/socket.h>
#	include <sys/types.h>
#	include <netinet/in.h>
#	include <arpa/inet.h>
#	include <net/if.h>
#	include <netdb.h>
#endif

#include <assert.h>
#include <map>
#include <vector>
#include <string>
#include <string.h>

#include "utils.h"

#ifndef WIN32
#ifdef	HAVE_IOCTL_H
#include <ioctl.h>
#else
#include <sys/ioctl.h>
#endif
#ifdef HAVE_SYS_SOCKIO_H
#include <sys/sockio.h>
#endif
#ifdef	HAVE_NET_IF_H
#include <net/if.h>
#endif
#endif

#ifdef __APPLE__
#include <ifaddrs.h>
#include <net/if_dl.h>
struct Tmp {
	std::string mac;
	std::string ipv4;
};
#endif

// 判断 mac 是否为虚拟机 mac
bool is_vm_mac(const char *mac)
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

	if (!mac)
		return true;	// FIXME:

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

// 将 byte[] 类型，转换为小写的 ascii 字符串.
static std::string conv_mac(unsigned char mac[], int len)
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

// 描述一个网卡配置.
struct NetInf {
	std::string name;	// 网卡名字 ..
	std::string macaddr;
	std::vector < std::string > ips;
};

static bool get_all_netinfs(std::vector < NetInf > &nis)
{
	static bool first = true;
	static std::vector < NetInf > _nis;

#ifdef WIN32
	if (first) {
		first = false;
		nis.clear();

		ULONG len = 16 * 1024;
		IP_ADAPTER_ADDRESSES *adapter =
		    (IP_ADAPTER_ADDRESSES *) malloc(len);

		// 仅仅 ipv4
		DWORD rc = GetAdaptersAddresses(AF_INET, 0, 0, adapter, &len);
		if (rc == ERROR_BUFFER_OVERFLOW) {
			adapter =
			    (IP_ADAPTER_ADDRESSES *) realloc(adapter, len);
			rc = GetAdaptersAddresses(AF_INET, 0, 0, adapter, &len);
		}

		if (rc == 0) {
			IP_ADAPTER_ADDRESSES *p = adapter;
			while (p) {
				if ((p->IfType == IF_TYPE_ETHERNET_CSMACD
				     || p->IfType == IF_TYPE_IEEE80211)
				    && (p->OperStatus == IfOperStatusUp)) {
					// 仅仅考虑 ethernet 或者 wifi，并且活动的.
					// 不包括虚拟机的 mac.
					std::string mac =
					    conv_mac(p->PhysicalAddress,
						     p->PhysicalAddressLength);
					if (!is_vm_mac(mac.c_str())) {
						NetInf ni;
						ni.macaddr = mac;

						// FIXME: 到底用哪个 :( .... 这里真混乱 ....
						//ni.name = p->AdapterName;
						//ni.name = (char*)bstr_t(p->FriendlyName);
						ni.name =
						    (char *)bstr_t(p->
								   Description);

						IP_ADAPTER_UNICAST_ADDRESS *ip =
						    p->FirstUnicastAddress;
						while (ip) {
							assert(ip->Address.
							       lpSockaddr->
							       sa_family ==
							       AF_INET);
							sockaddr_in *addr =
							    (sockaddr_in *) ip->
							    Address.lpSockaddr;
							ni.ips.
							    push_back(inet_ntoa
								      (addr->
								       sin_addr));

							ip = ip->Next;
						}

						nis.push_back(ni);
					}
				}
				p = p->Next;
			}

			free(adapter);
		}

		_nis = nis;
	} else {
		nis = _nis;
	}
#endif				// win32

#ifdef __APPLE__
	struct ifaddrs *ifap, *ifa;
	std::map < std::string, Tmp > name_macs;
	std::map < std::string, Tmp >::iterator itf;

	if (getifaddrs(&ifap) == 0 && ifap) {
		for (ifa = ifap; ifa; ifa = ifa->ifa_next) {
			if (ifa->ifa_flags & IFF_LOOPBACK)
				continue;
			if (!(ifa->ifa_flags & IFF_RUNNING))
				continue;

			if (strstr(ifa->ifa_name, "bridge"))	// 去除桥接网卡 .
				continue;

			fprintf(stderr, "name: %s, family=%d\n", ifa->ifa_name,
				ifa->ifa_addr->sa_family);
			if (ifa->ifa_addr
			    && ifa->ifa_addr->sa_family == AF_LINK) {
				/* Link layer interface */
				struct sockaddr_dl *dl =
				    (struct sockaddr_dl *)ifa->ifa_addr;
				unsigned char *p = (unsigned char *)LLADDR(dl);
				std::string mac = conv_mac(p, dl->sdl_alen);
				if (!is_vm_mac(mac.c_str())) {
					itf = name_macs.find(ifa->ifa_name);
					if (itf == name_macs.end()) {
						Tmp tmp;
						tmp.mac = mac;
						name_macs[ifa->ifa_name] = tmp;
					} else {
						itf->second.mac = mac;
					}
				}
			}

			if (ifa->ifa_addr
			    && ifa->ifa_addr->sa_family == AF_INET) {
				// IPV4
				struct sockaddr_in *sin =
				    (struct sockaddr_in *)ifa->ifa_addr;
				std::string ip = inet_ntoa(sin->sin_addr);
				itf = name_macs.find(ifa->ifa_name);
				if (itf == name_macs.end()) {
					Tmp tmp;
					tmp.ipv4 = ip;
					name_macs[ifa->ifa_name] = tmp;
				} else {
					itf->second.ipv4 = ip;
				}
			}
		}

		for (itf = name_macs.begin(); itf != name_macs.end(); ++itf) {
			Tmp & tmp = itf->second;
			if (!tmp.mac.empty() && !tmp.ipv4.empty()) {
				NetInf ni;
				ni.macaddr = tmp.mac;
				ni.ips.push_back(tmp.ipv4);

				nis.push_back(ni);
			}
		}

		freeifaddrs(ifap);
	}
#endif				// apple
#ifdef linux

	if (!first) {
		nis = _nis;
		return true;
	}

	char buf[8096];
	struct ifconf ifc;

	int fd = socket(AF_INET, SOCK_DGRAM, 0);
	if (fd == -1)
		return false;

	ifc.ifc_len = sizeof(buf);
	ifc.ifc_buf = buf;

	if (ioctl(fd, SIOCGIFCONF, &ifc) == -1)
		return false;

	int n = ifc.ifc_len / sizeof(ifreq);
	for (int i = 0; i < n; i++) {
		ifreq *req = (ifreq *) & buf[i * sizeof(ifreq)];
		const char *name = req->ifr_name;

		if (!strcmp(name, "lo"))
			continue;

		ioctl(fd, SIOCGIFFLAGS, (char *)req);
		if (!(req->ifr_flags & IFF_UP))
			continue;

		ioctl(fd, SIOCGIFHWADDR, (char *)req);
		std::string mac =
		    conv_mac((uint8_t *) req->ifr_hwaddr.sa_data, 6);

		ioctl(fd, SIOCGIFADDR, (char *)req);
		sockaddr_in *sin = (sockaddr_in *) & req->ifr_addr;

		if (sin->sin_family != AF_INET)
			continue;

		NetInf ni;
		ni.name = name;
		ni.macaddr = mac;
		ni.ips.push_back(inet_ntoa(sin->sin_addr));

		nis.push_back(ni);
	}

	close(fd);

	_nis = nis;
#endif

	return true;
}

const char *util_get_myip()
{
	char *p = getenv("zonekey_my_ip");
	if (p)
		return p;

	static std::string _ip;
	if (_ip.empty()) {
		std::vector < NetInf > nis;
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

const char *util_get_myip_real()
{
	char *p = getenv("zonekey_my_ip_real");
	if (p)
		return p;

	static std::string _ip;
	if (_ip.empty()) {
		std::vector < NetInf > nis;
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

const char *util_get_mymac()
{
	char *p = getenv("zonekey_my_mac");
	if (p)
		return p;

	static std::string _mac;
	if (_mac.empty()) {
		std::vector < NetInf > nis;
		get_all_netinfs(nis);
		if (nis.size() > 0) {
			_mac = nis[0].macaddr;
		}
	}

	if (_mac.empty())
		_mac = "000000000000";
	return _mac.c_str();
}

const char *util_get_nic_name()
{
	char *p = getenv("zonekey_my_nic");
	if (p)
		return p;

	static std::string _nic_name;
	if (_nic_name.empty()) {
		std::vector < NetInf > nis;
		get_all_netinfs(nis);
		if (nis.size() > 0) {
			_nic_name = nis[0].name;
		}
	}

	if (_nic_name.empty())
		_nic_name = "unknown";

	return _nic_name.c_str();
}

