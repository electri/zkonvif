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

#ifdef __APPLE__
#include <CoreFoundation/CoreFoundation.h>
 
#include <IOKit/IOKitLib.h>
#include <IOKit/network/IOEthernetInterface.h>
#include <IOKit/network/IONetworkInterface.h>
#include <IOKit/network/IOEthernetController.h>
 
static kern_return_t FindEthernetInterfaces(io_iterator_t *matchingServices);
static kern_return_t GetMACAddress(io_iterator_t intfIterator, UInt8 *MACAddress, UInt8 bufferSize);
 
// Returns an iterator containing the primary (built-in) Ethernet interface. The caller is responsible for
// releasing the iterator after the caller is done with it.
static kern_return_t FindEthernetInterfaces(io_iterator_t *matchingServices)
{
    kern_return_t           kernResult; 
    CFMutableDictionaryRef  matchingDict;
    CFMutableDictionaryRef  propertyMatchDict;
    
    // Ethernet interfaces are instances of class kIOEthernetInterfaceClass. 
    // IOServiceMatching is a convenience function to create a dictionary with the key kIOProviderClassKey and 
    // the specified value.
    matchingDict = IOServiceMatching(kIOEthernetInterfaceClass);
 
    // Note that another option here would be:
    // matchingDict = IOBSDMatching("en0");
    // but en0: isn't necessarily the primary interface, especially on systems with multiple Ethernet ports.
        
    if (NULL == matchingDict) {
        printf("IOServiceMatching returned a NULL dictionary.\n");
    }
    else {
        // Each IONetworkInterface object has a Boolean property with the key kIOPrimaryInterface. Only the
        // primary (built-in) interface has this property set to TRUE.
        
        // IOServiceGetMatchingServices uses the default matching criteria defined by IOService. This considers
        // only the following properties plus any family-specific matching in this order of precedence 
        // (see IOService::passiveMatch):
        //
        // kIOProviderClassKey (IOServiceMatching)
        // kIONameMatchKey (IOServiceNameMatching)
        // kIOPropertyMatchKey
        // kIOPathMatchKey
        // kIOMatchedServiceCountKey
        // family-specific matching
        // kIOBSDNameKey (IOBSDNameMatching)
        // kIOLocationMatchKey
        
        // The IONetworkingFamily does not define any family-specific matching. This means that in            
        // order to have IOServiceGetMatchingServices consider the kIOPrimaryInterface property, we must
        // add that property to a separate dictionary and then add that to our matching dictionary
        // specifying kIOPropertyMatchKey.
            
        propertyMatchDict = CFDictionaryCreateMutable(kCFAllocatorDefault, 0,
                                                      &kCFTypeDictionaryKeyCallBacks,
                                                      &kCFTypeDictionaryValueCallBacks);
    
        if (NULL == propertyMatchDict) {
            printf("CFDictionaryCreateMutable returned a NULL dictionary.\n");
        }
        else {
            // Set the value in the dictionary of the property with the given key, or add the key 
            // to the dictionary if it doesn't exist. This call retains the value object passed in.
            CFDictionarySetValue(propertyMatchDict, CFSTR(kIOPrimaryInterface), kCFBooleanTrue); 
            
            // Now add the dictionary containing the matching value for kIOPrimaryInterface to our main
            // matching dictionary. This call will retain propertyMatchDict, so we can release our reference 
            // on propertyMatchDict after adding it to matchingDict.
            CFDictionarySetValue(matchingDict, CFSTR(kIOPropertyMatchKey), propertyMatchDict);
            CFRelease(propertyMatchDict);
        }
    }
    
    // IOServiceGetMatchingServices retains the returned iterator, so release the iterator when we're done with it.
    // IOServiceGetMatchingServices also consumes a reference on the matching dictionary so we don't need to release
    // the dictionary explicitly.
    kernResult = IOServiceGetMatchingServices(kIOMasterPortDefault, matchingDict, matchingServices);    
    if (KERN_SUCCESS != kernResult) {
        printf("IOServiceGetMatchingServices returned 0x%08x\n", kernResult);
    }
        
    return kernResult;
}
    
// Given an iterator across a set of Ethernet interfaces, return the MAC address of the last one.
// If no interfaces are found the MAC address is set to an empty string.
// In this sample the iterator should contain just the primary interface.
static kern_return_t GetMACAddress(io_iterator_t intfIterator, UInt8 *MACAddress, UInt8 bufferSize)
{
    io_object_t     intfService;
    io_object_t     controllerService;
    kern_return_t   kernResult = KERN_FAILURE;
    
    // Make sure the caller provided enough buffer space. Protect against buffer overflow problems.
    if (bufferSize < kIOEthernetAddressSize) {
        return kernResult;
    }
    
    // Initialize the returned address
    bzero(MACAddress, bufferSize);
    
    // IOIteratorNext retains the returned object, so release it when we're done with it.
    while ((intfService = IOIteratorNext(intfIterator)))
    {
        CFTypeRef   MACAddressAsCFData;        
 
        // IONetworkControllers can't be found directly by the IOServiceGetMatchingServices call, 
        // since they are hardware nubs and do not participate in driver matching. In other words,
        // registerService() is never called on them. So we've found the IONetworkInterface and will 
        // get its parent controller by asking for it specifically.
        
        // IORegistryEntryGetParentEntry retains the returned object, so release it when we're done with it.
        kernResult = IORegistryEntryGetParentEntry(intfService,
                                                   kIOServicePlane,
                                                   &controllerService);
        
        if (KERN_SUCCESS != kernResult) {
            printf("IORegistryEntryGetParentEntry returned 0x%08x\n", kernResult);
        }
        else {
            // Retrieve the MAC address property from the I/O Registry in the form of a CFData
            MACAddressAsCFData = IORegistryEntryCreateCFProperty(controllerService,
                                                                 CFSTR(kIOMACAddress),
                                                                 kCFAllocatorDefault,
                                                                 0);
            if (MACAddressAsCFData) {
                CFShow(MACAddressAsCFData); // for display purposes only; output goes to stderr
                
                // Get the raw bytes of the MAC address from the CFData
                CFDataGetBytes((CFDataRef)MACAddressAsCFData, CFRangeMake(0, kIOEthernetAddressSize), MACAddress);
                CFRelease(MACAddressAsCFData);
            }
                
            // Done with the parent Ethernet controller object so we release it.
            (void) IOObjectRelease(controllerService);
        }
        
		// Done with the Ethernet interface object so we release it.
		(void) IOObjectRelease(intfService);
	}

	return kernResult;
}

static std::string osx_get_mac()
{
		std::string mac = "000000000000";
		kern_return_t   kernResult = KERN_SUCCESS;
		io_iterator_t   intfIterator;
		UInt8           MACAddress[kIOEthernetAddressSize];

		kernResult = FindEthernetInterfaces(&intfIterator);

		if (KERN_SUCCESS != kernResult) {
				printf("FindEthernetInterfaces returned 0x%08x\n", kernResult);
		}
		else {
				kernResult = GetMACAddress(intfIterator, MACAddress, sizeof(MACAddress));

				if (KERN_SUCCESS != kernResult) {
						printf("GetMACAddress returned 0x%08x\n", kernResult);
				}
				else {
						char buf[16];
						sprintf(buf, "%02x%02x%02x%02x%02x%02x",
								MACAddress[0], MACAddress[1], MACAddress[2], 
								MACAddress[3], MACAddress[4], MACAddress[5]);
						mac = buf;
				}
		}

		(void) IOObjectRelease(intfIterator);   // Release the iterator.
		return mac;
}

#endif // 

// 判断 mac 是否为虚拟机 mac
static bool is_vm_mac(const char *mac)
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

		"0a1196",	// Microsoft 托管网络虚拟适配器 ？？
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
struct NetInf
{
	std::string macaddr;
	std::vector<std::string> ips;
};

/** 获取可用网卡配置，仅仅选择启动的 ipv4的，非虚拟机的，ethernet
*/
static bool get_all_netinfs(std::vector<NetInf> &nis)
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

        
        fprintf(stderr, "if: name=%s, ip=%s\n", req->ifr_name, inet_ntoa(sin.sin_addr));
        
        NetInf ni;
        ni.macaddr = req->ifr_name;
        ni.ips.push_back(inet_ntoa(sin.sin_addr));

		nis.push_back(ni);
    }

	close(fd);
#endif
    
	return true;
}

static ost::Mutex _cs;

static std::string _ipreal;
const char *util_get_myip_real()
{
	ost::MutexLock al(_cs);

	char *p = getenv("zonekey_my_ip_real");
	if (p) return p;

	if (_ipreal.empty()) {
		std::vector<NetInf> nis;
		get_all_netinfs(nis);
		if (nis.size() > 0) {
			if (nis[0].ips.size() > 0) {
				_ipreal = nis[0].ips[0];
			}
		}
	}

	if (_ipreal.empty())
		_ipreal = "000.000.000.000";
	return _ipreal.c_str();
}

static std::string _ip;
static std::string _mac;

const char *util_get_myip()
{
	ost::MutexLock al(_cs);

	char *p = getenv("zonekey_my_ip");
	if (p) return p;

	if (_ip.empty()) {
		std::vector<NetInf> nis;
		get_all_netinfs(nis);
		if (nis.size() > 0) {
			if (nis[0].ips.size() > 0) {
				_ip = nis[0].ips[0];
				_mac = nis[0].macaddr;
			}
		}
	}

	if (_ip.empty())
		_ip = "000.000.000.000";
	return _ip.c_str();
}

const char *util_get_mymac()
{
	ost::MutexLock al(_cs);

	char *p = getenv("zonekey_my_mac");
	if (p) return p;

	if (_mac.empty()) {
#ifdef __APPLE__
		_mac = osx_get_mac();
#else
		std::vector<NetInf> nis;
		get_all_netinfs(nis);
		if (nis.size() > 0) {
			_mac = nis[0].macaddr;
			_ip = nis[0].ips[0];
		}
#endif
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