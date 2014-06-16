#pragma once

#include <assert.h>
#include <cc++/socket.h>
#include <cc++/network.h>
#include <cc++/address.h>
#include <map>
#include <string>
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

#ifdef __APPLE__
#  include <ifaddrs.h>
#  include <net/if_dl.h>
struct Tmp
{
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

// 将 byte[] 类型，转换为小写的 ascii 字符串.
std::string conv_mac(unsigned char mac[], int len)
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
struct NetInf
{
	std::string macaddr;
	std::vector<std::string> ips;
};

/** 获取可用网卡配置，仅仅选择启动的 ipv4的，非虚拟机的，ethernet
 */
bool get_all_netinfs(std::vector<NetInf> &nis)
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
				// 仅仅考虑 ethernet 或者 wifi，并且活动的.
				// 不包括虚拟机的 mac.
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
    
#elif __APPLE__
    struct ifaddrs *ifap, *ifa;
    std::map<std::string, Tmp> name_macs;
    std::map<std::string, Tmp>::iterator itf;
    
    if (getifaddrs(&ifap) == 0 && ifap) {
        for (ifa = ifap; ifa; ifa = ifa->ifa_next) {
            if (ifa->ifa_flags & IFF_LOOPBACK)
                continue;
            if (!(ifa->ifa_flags & IFF_RUNNING))
                continue;
            
            if (strstr(ifa->ifa_name, "bridge")) // 去除桥接网卡
                continue;
            
            fprintf(stderr, "name: %s, family=%d\n", ifa->ifa_name, ifa->ifa_addr->sa_family);
            if (ifa->ifa_addr && ifa->ifa_addr->sa_family == AF_LINK) {
                /* Link layer interface */
                struct sockaddr_dl *dl = (struct sockaddr_dl*)ifa->ifa_addr;
                unsigned char *p = (unsigned char*)LLADDR(dl);
                std::string mac = conv_mac(p, dl->sdl_alen);
                if (!is_vm_mac(mac.c_str())) {
                    itf = name_macs.find(ifa->ifa_name);
                    if (itf == name_macs.end()) {
                        Tmp tmp;
                        tmp.mac = mac;
                        name_macs[ifa->ifa_name] = tmp;
                    }
                    else {
                        itf->second.mac = mac;
                    }
                }
            }
            
            if (ifa->ifa_addr && ifa->ifa_addr->sa_family == AF_INET) {
                // IPV4
                struct sockaddr_in *sin = (struct sockaddr_in*)ifa->ifa_addr;
                std::string ip = inet_ntoa(sin->sin_addr);
                itf = name_macs.find(ifa->ifa_name);
                if (itf == name_macs.end()) {
                    Tmp tmp;
                    tmp.ipv4 = ip;
                    name_macs[ifa->ifa_name] = tmp;
                }
                else {
                    itf->second.ipv4 = ip;
                }
            }
        }
        
        for (itf = name_macs.begin(); itf != name_macs.end(); ++itf) {
            Tmp &tmp = itf->second;
            if (!tmp.mac.empty() && !tmp.ipv4.empty()) {
                NetInf ni;
                ni.macaddr = tmp.mac;
                ni.ips.push_back(tmp.ipv4);
                
                nis.push_back(ni);
            }
        }
        
        freeifaddrs(ifap);
    }
#else
	char buffer[8096];
	struct ifconf ifc;
    
	int fd = socket(AF_INET, SOCK_DGRAM, 0);
	if (fd == -1)
		return false;
    
	ifc.ifc_len = sizeof(buffer);
	ifc.ifc_buf = buffer;
    
	if (ioctl(fd, SIOCGIFCONF, &ifc) == -1)
		return false;
    
    for (char *ptr = buffer; ptr < buffer + ifc.ifc_len; ) {
        ifreq *req = (ifreq*)ptr;
        int len = sizeof(sockaddr) > req->ifr_addr.sa_len ? sizeof(sockaddr) : req->ifr_addr.sa_len;
        
        ptr += sizeof(req->ifr_name) + len; // next
        
        if (req->ifr_addr.sa_family != AF_INET)
            continue;
        
        ioctl(fd, SIOCGIFFLAGS, req);
        int flags = req->ifr_flags;
        if (flags & IFF_LOOPBACK)
            continue;
        
        if (!(flags & IFF_UP))
            continue;
        
        sockaddr_in sin;
        sin.sin_addr = ((sockaddr_in&)req->ifr_addr).sin_addr;
        
        ioctl(fd, SIOCGIFHWADDR, req);
        uint8_t *mac = (uint8_t*)req->ifr_hwaddr.sa_data;
        
        NetInf ni;
        ni.macaddr = conv_mac(mac, 6);
        ni.ips.push_back(inet_ntoa(sin.sin_addr));
        
        fprintf(stderr, "if: name=%s, ip=%s, mac=%s\n", req->ifr_name, inet_ntoa(sin.sin_addr), ni.macaddr.c_str());
    }
    
	close(fd);
#endif
    
	return true;
}

const char *util_get_myip_real()
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

const char *util_get_myip()
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

const char *util_get_mymac()
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


#include "../libzkonvif/soap/soapH.h"

/** 
@fn const char *soap_wsa_rand_uuid(struct soap *soap)
@brief Generates a random UUID(UUID algorithm version 4).
@param soap context
@return UUID "urn:uid:xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxx"
*/

const char* soap_wsa_rand_uuid(struct soap *soap)
{
	const int uuidlen = 48;
	char *uuid = (char*)soap_malloc(soap, uuidlen);
	int r1, r2, r3, r4;
#ifdef WITH_OPENSSL
	r1 = soap_random;
	r2 = soap_randome;
#else
	static int k = 0xFACEB00B;
	int lo = k % 127773;
	int hi = k / 127773;
#	ifndef WIN32
	struct timeval tv;
	gettimeofday(&tv, NULL);
	r1 = 10000000 * tv.tv_sec + tv.tv_usec;
#else
	r1 = (int)time(NULL);
#	endif
	k = 16807 * lo - 2836 * hi;
	if (k <= 0)
		k += 0x7FFFFFFF;
	r2 = k;
	k &= 0x8FFFFFFF;
	r2 += *(int*)soap->buf;
#endif
	r3 = soap_random;
	r4 = soap_random;
#ifdef HAVE_SNPRINTF
	soap_snprintf(uuid, uuidlen, "urn:uuid:%8.8x-%4.4hx-4%3.3hx-%4.4hx-%8.8x",
		r1,
		(short)(r2 >> 16),
		((short)r2 >> 4) & 0x0FFF,
		((short)(r3 >> 16) & 0x3FFF),
		(short)r3,
		r4);
#else
	snprintf(uuid, uuidlen, "urn:uuid:%8.8x-%4.4hx-4%3.3hx-%4.4hx-%8.8x",
		r1,
		(short)(r2 >> 16),
		((short)r2 >> 4) & 0x0FFF,
		((short)(r3 >> 16) & 0x3FFF),
		(short)r3,
		r4);
#endif
	//DEGFUN1("soap_wsa_rand_uuid", "%s", uuid);
	return uuid;
}
