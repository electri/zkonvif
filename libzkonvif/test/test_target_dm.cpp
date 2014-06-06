/**	Zonekey Source:
		实现 target 端的 device mgrt 接口
 */

#include <cc++/thread.h>
#include <sstream>
#include <string>
#include "../soap/soapDeviceBindingService.h"
#include "../soap/soapwsddService.h"
#include <assert.h>
#include "../../common/utils.h"
#include "../../common/log.h"

/** 实现一个接口，本质就是重载 gsoap 生成的 xxxxService 类，然后具体实现所有“纯虚函数”即可; 
 */
class MyDevice : DeviceBindingService
			   , ost::Thread
{
	int listen_port_;
	std::string url_;
	std::string id_;

public:
	MyDevice(int listen_port)
	{
		listen_port_ = listen_port;
		char buf[128];

		snprintf(buf, sizeof(buf), "http://%s:%d", util_get_myip(), listen_port_);
		url_ = buf;

		/** 使用 mac 地址作为 id */
		snprintf(buf, sizeof(buf), "urn:uuid:%s", util_get_mymac());
		id_ = buf;

		start();	// 启动工作线程. 
	}

	const char *id() const { return id_.c_str(); }
	const char *url() const { return url_.c_str(); }

private:
	void run()
	{
		DeviceBindingService::run(listen_port_);
	}

private:
	/// 下面实现 device mgrt 接口，.....

	
};

static FILE *_fp;

/** 设备发现，用于声明 MyDevice 接口
 */
class MyDeviceDiscovery : wsddService
					    , ost::Thread
{
	const MyDevice *device_;

public:
	MyDeviceDiscovery(const MyDevice *device) : wsddService(SOAP_IO_UDP)	// 总是 udp 模式
	{
		device_ = device;

		start();	// 启动工作线程.
	}

private:
	void run()
	{
		// 加入组播地址，绑定 3702 端口
#define PORT 3702
#define ADDR "239.255.255.250"

		soap->bind_flags |= SO_REUSEADDR;
		if (!soap_valid_socket(bind(0, PORT, 100))) {
			log(LOG_FAULT, "%s: bind %d err\n", PORT);
			::exit(-1);
		}

		ip_mreq req;
		const char *ip = util_get_myip();
		req.imr_interface.s_addr = inet_addr(ip);
		req.imr_multiaddr.s_addr = inet_addr(ADDR);

		if (setsockopt(soap->master, IPPROTO_IP, IP_ADD_MEMBERSHIP, (char*)&req, sizeof(req)) < 0) {
			log(LOG_FAULT, "%s: can't join multiaddr!\n", __func__);
			::exit(-1);
		}

		log(LOG_DEBUG, "%s: en, using local ip '%s' waiting incoming ...\n", __func__, ip);

		while (1) {
			serve();
			soap_destroy(soap);
			soap_end(soap);
		}
	}

private:
	static const char *my_messageid()
	{
		static int _i = 0;
		static char buf[64];

		snprintf(buf, sizeof(buf), "id:%u", _i++);

		return buf;
	}

	virtual int Probe(struct wsdd__ProbeType *probe)
	{
		/** Probe: 如果 tds，则返回 MyDevice 的  url ...
		 */
		// 根据 targets 构造 ProbeMatches ...
		log(LOG_DEBUG, "%s: 'Probe' incoming: types=%s\n", __func__, probe->Types);
		if (!strcmp("tds:Device", probe->Types) || !strcmp("tdn:NetworkVideoTransmitter", probe->Types)) {
			wsdd__ProbeMatchesType pms;
			pms.__sizeProbeMatch = 1;
			pms.ProbeMatch = (wsdd__ProbeMatchType*)soap_malloc(soap, 1 * sizeof(wsdd__ProbeMatchType));
			wsdd__ProbeMatchType *pm = &pms.ProbeMatch[0];

			// 填空 ..
			pm->wsa__EndpointReference.Address = soap_strdup(soap, device_->id());
			pm->wsa__EndpointReference.ReferenceParameters = 0;
			pm->wsa__EndpointReference.ReferenceProperties = 0;
			pm->wsa__EndpointReference.PortType = 0;
			pm->wsa__EndpointReference.ServiceName = 0;
			pm->wsa__EndpointReference.__size = 0;
			pm->wsa__EndpointReference.__any = 0;
			pm->wsa__EndpointReference.__anyAttribute = 0;

			pm->Types = soap_strdup(soap, "tdn:NetworkVideoTransmitter");

			pm->Scopes = (wsdd__ScopesType*)soap_malloc(soap, sizeof(wsdd__ScopesType));
			pm->Scopes->MatchBy = 0;
			pm->Scopes->__item = soap_strdup(soap, "onvif://www.onvif.org/type/NetworkVideoTransmitter");

			pm->XAddrs = soap_strdup(soap, device_->url());

			pm->MetadataVersion = 1;

			// 需要修改 wsa_Header
			SOAP_ENV__Header * header = soap->header;
			assert(header);

			// XXX: 必须的，否则 client 不知道这个 PM 是对应着那个 P
			header->wsa__RelatesTo = (wsa__Relationship *)soap_malloc(soap, sizeof(wsa__Relationship));
			header->wsa__RelatesTo->__item = soap_strdup(soap, header->wsa__MessageID);
			header->wsa__RelatesTo->__anyAttribute = 0;
			header->wsa__RelatesTo->RelationshipType = 0;

			header->wsa__MessageID = soap_strdup(soap, my_messageid());
			header->wsa__To = 0; // soap_strdup(soap, "http://schemas.xmlsoap.org/ws/2004/08/addressing/role/anonymous");
			header->wsa__Action = 0; // soap_strdup(soap, "http://schemas.xmlsoap.org/ws/2005/04/discovery/ProbeMatches");

			_fp = fopen("pm.xml", "w");
			soap->fpreparesend = debug_before_send;
			__send_ProbeMatches(soap, "http://", 0, &pms);
			soap->fpreparesend = 0;
			fclose(_fp);
			_fp = 0;
		}

		return SOAP_OK;
	}

	static int debug_before_send(struct soap *soap, const char *data, size_t len)
	{
		if (_fp) {
			fprintf(_fp, "%s", data);
		}

		return 0;
	}


	// 下面这段代码从 soapwsddProxy.cpp 中复制的，稍加修改 :)
	// 声明为 static 的目的是防止使用 members
	static int __send_ProbeMatches(struct soap *soap, const char *soap_endpoint, const char *soap_action, struct wsdd__ProbeMatchesType *wsdd__ProbeMatches)
	{
		struct __wsdd__ProbeMatches soap_tmp___wsdd__ProbeMatches;

		if (soap_action == NULL)
			soap_action = "http://docs.oasis-open.org/ws-dd/ns/discovery/2009/01/ProbeMatches";
		soap_begin(soap);
		soap->encodingStyle = NULL;
		soap_tmp___wsdd__ProbeMatches.wsdd__ProbeMatches = wsdd__ProbeMatches;
		soap_serializeheader(soap);
		soap_serialize___wsdd__ProbeMatches(soap, &soap_tmp___wsdd__ProbeMatches);
		if (soap_begin_count(soap))
			return soap->error;
		if (soap->mode & SOAP_IO_LENGTH)
		{
			if (soap_envelope_begin_out(soap)
				|| soap_putheader(soap)
				|| soap_body_begin_out(soap)
				|| soap_put___wsdd__ProbeMatches(soap, &soap_tmp___wsdd__ProbeMatches, "-wsdd:ProbeMatches", NULL)
				|| soap_body_end_out(soap)
				|| soap_envelope_end_out(soap))
				return soap->error;
		}
		if (soap_end_count(soap))
			return soap->error;
		if (soap_connect(soap, soap_url(soap, soap_endpoint, NULL), soap_action)
			|| soap_envelope_begin_out(soap)
			|| soap_putheader(soap)
			|| soap_body_begin_out(soap)
			|| soap_put___wsdd__ProbeMatches(soap, &soap_tmp___wsdd__ProbeMatches, "-wsdd:ProbeMatches", NULL)
			|| soap_body_end_out(soap)
			|| soap_envelope_end_out(soap)
			|| soap_end_send(soap))
			return soap_closesock(soap);
		return SOAP_OK;
	}
};

int main(int argc, char **argv)
{
	log_init();

	MyDevice device(9999);
	MyDeviceDiscovery discovery(&device);

	while (1) {
		ost::Thread::sleep(100);
	}

	return 0;
}
