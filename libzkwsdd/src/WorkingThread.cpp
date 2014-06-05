#include "utils.h"
#include "WorkingThread.h"
#include "../soap/soapH.h"
#include <algorithm>
#include "log.h"

void send_hello(Target *target);
void send_bye(Target *target);

TargetThread::TargetThread()
{
	quit_ = false;
	start();
}

TargetThread::~TargetThread()
{
	quit_ = true;
	join();
}

int TargetThread::bind(Target *target)
{
    ost::MutexLock al(cs_fifo_);
	fifo_.push_back(target);

    send_hello(target); // multicast方式  发送 hello

	return (int)fifo_.size();
}

int TargetThread::unbind(Target *target)
{
	send_bye(target); // multicast 方式 发送 bye
    
    ost::MutexLock al(cs_fifo_);
    FIFO::iterator itend = std::remove(fifo_.begin(), fifo_.end(), target);
	fifo_.erase(itend, fifo_.end());

	return (int)fifo_.size();
}

#define MULTI_ADDR "239.255.255.250"
#define PORT 3702

void TargetThread::run()
{
	log(LOG_INFO, "%s: Target thread started!\n", __func__);

	/** Target 工作线程加入组播地址，开始接受数据 ....
	 */
	soap soap;
	soap_init1(&soap, SOAP_IO_UDP);
	
	soap.user = new ThreadOpaque("target", this);
	soap.bind_flags = SO_REUSEADDR;		// 可能多个 ...

	if (!soap_valid_socket(soap_bind(&soap, 0, PORT, 100))) {
		log(LOG_FAULT, "%s: soap_bind %d failure!!\n", __func__, PORT);
		::exit(-1);
	}

	ip_mreq mcast;
	mcast.imr_multiaddr.s_addr = inet_addr(MULTI_ADDR);
	mcast.imr_interface.s_addr = inet_addr(util_get_myip());
	if (setsockopt(soap.master, IPPROTO_IP, IP_ADD_MEMBERSHIP, (char*)&mcast, sizeof(mcast)) < 0) {
		log(LOG_FAULT, "%s: ohhh, can't join multiaddr of %s!!!!\n", __func__, MULTI_ADDR);
		::exit(-1);
	}

	while (!quit_) {
		soap_serve(&soap);	// udp 接收阻塞在此. 
		soap_destroy(&soap);
		soap_end(&soap);
	}

    // * 发送bye, 以 muticast 方式
	soap_done(&soap);

	log(LOG_INFO, "%s: thread terminated!\n", __func__);
}

std::vector<Target*> TargetThread::probe_matched(const char *types, const char *scopes)
{
	std::vector<Target *> targets;
	ost::MutexLock al(cs_fifo_);

	FIFO::const_iterator it;
	for (it = fifo_.begin(); it != fifo_.end(); ++it) {
		// TODO: 这里进行 types, scopes 的匹配 ...

		targets.push_back(*it);
	}

	return targets;
}

static const char *my_messageid()
{
	static int _i = 0;
	static char buf[64];
    
	snprintf(buf, sizeof(buf), "id:%u", _i++);
    
	return buf;
}


void send_hello(Target *target)
{
    soap soap;
    soap.send_timeout = 1;
	soap_init1(&soap, SOAP_IO_UDP);
	
	soap.bind_flags = SO_REUSEADDR;
    
	if (!soap_valid_socket(soap_bind(&soap, 0, PORT, 100))) {
		log(LOG_FAULT, "%s: soap_bind %d failure!!\n", __func__, PORT);
		::exit(-1);
	}
    
	ip_mreq mcast;
	mcast.imr_multiaddr.s_addr = inet_addr(MULTI_ADDR);
	mcast.imr_interface.s_addr = inet_addr(util_get_myip());
	if (setsockopt(soap.master, IPPROTO_IP, IP_ADD_MEMBERSHIP, (char*)&mcast, sizeof(mcast)) < 0) {
		log(LOG_FAULT, "%s: ohhh, can't join multiaddr of %s!!!!\n", __func__, MULTI_ADDR);
		::exit(-1);
	}
    
    struct wsdd__HelloType *wsdd_hello = (struct wsdd__HelloType*)soap_malloc(&soap, sizeof(struct wsdd__HelloType));
    
    wsdd_hello->Scopes = NULL;
    wsdd_hello->Types = soap_strdup(&soap, target->type());
    
    //FIXME:下面这行，赋值方式 有可能 错误
    wsdd_hello->MetadataVersion = atoi(my_messageid()); // maybe mistake
    wsdd_hello->wsa__EndpointReference.Address = soap_strdup(&soap, target->id());
    
    // header
    
    struct SOAP_ENV__Header header;
    soap_default_SOAP_ENV__Header(&soap, &header); // init SOAP Header
    
    header.wsa__Action = soap_strdup(&soap, "http://docs.oasis-open.org/ws-dd/ns/discovery/2009/01/Hello"); // mustUnderstand
    header.wsa__To = soap_strdup(&soap, "urn:docs-oasis-open-org:ws-dd:ns:discovery:2009:01"); //mustUnderstand
    header.wsa__ReplyTo = NULL; //mustUnderst
    header.wsdd__AppSequence = NULL; // optional
    header.wsa__From = NULL; // optional
    header.wsa__RelatesTo = NULL; //optional
    header.wsa__MessageID = NULL; // optional
    
    soap.header = &header;
    
    if (soap_send___wsdd__Hello(&soap, "http://", NULL, wsdd_hello) != SOAP_OK)
        soap_print_fault(&soap, stderr); // report error

    soap_destroy(&soap); // cleanup
    soap_end(&soap); // cleanup
    soap_done(&soap); // close connection (should not use soap struct after this)
    
}


void send_bye(Target *target)
{
    soap soap;
    soap.send_timeout = 1;
	soap_init1(&soap, SOAP_IO_UDP);
	
	soap.bind_flags = SO_REUSEADDR;
    
	if (!soap_valid_socket(soap_bind(&soap, 0, PORT, 100))) {
		log(LOG_FAULT, "%s: soap_bind %d failure!!\n", __func__, PORT);
		::exit(-1);
	}
    
	ip_mreq mcast;
	mcast.imr_multiaddr.s_addr = inet_addr(MULTI_ADDR);
	mcast.imr_interface.s_addr = inet_addr(util_get_myip());
	if (setsockopt(soap.master, IPPROTO_IP, IP_ADD_MEMBERSHIP, (char*)&mcast, sizeof(mcast)) < 0) {
		log(LOG_FAULT, "%s: ohhh, can't join multiaddr of %s!!!!\n", __func__, MULTI_ADDR);
		::exit(-1);
	}
    
    //FIXME: version 有可能 错误
    unsigned int version = atoi(my_messageid()); // maybe mistake
    
    struct wsdd__ByeType *wsdd_bye = (struct wsdd__ByeType*)soap_malloc(&soap, sizeof(struct wsdd__ByeType));
    wsdd_bye->wsa__EndpointReference.Address = soap_strdup(&soap, target->id());
    wsdd_bye->MetadataVersion = &version;
    
    if (soap_send___wsdd__Bye(&soap, "soap.udp://...", NULL, wsdd_bye) != SOAP_OK)
        soap_print_fault(&soap, stderr); //report error
    

    // header
    
    struct SOAP_ENV__Header header;
    soap_default_SOAP_ENV__Header(&soap, &header); // init SOAP Header
    
    header.wsa__Action = soap_strdup(&soap, "http://docs.oasis-open.org/ws-dd/ns/discovery/2009/01/Bye"); // mustUnderstand
    header.wsa__To = soap_strdup(&soap, "urn:docs-oasis-open-org:ws-dd:ns:discovery:2009:01");//mustUnderstand
    header.wsa__ReplyTo = NULL; //mustUnderst
    header.wsdd__AppSequence = NULL; // optional
    header.wsa__From = NULL; // optional
    header.wsa__RelatesTo = NULL; //optional
    header.wsa__MessageID = NULL; // optional
    
    soap.header = &header;
    
    if (soap_send___wsdd__Bye(&soap, "http://", NULL, wsdd_bye) != SOAP_OK)
        soap_print_fault(&soap, stderr); // report error
    
    soap_destroy(&soap); // cleanup
    soap_end(&soap); // cleanup
    soap_done(&soap); // close connection (should not use soap struct after this)
    
}

std::vector<Target*> TargetThread::resolve_matched(const char *address)
{
	std::vector<Target *> targets;
	ost::MutexLock al(cs_fifo_);

	FIFO::const_iterator it;
	for (it = fifo_.begin(); it != fifo_.end(); ++it) {
		//这里进行 address 的匹配 ...
		Target *t = *it;
		if (t->id()==address)
		{
			targets.push_back(*it);
		}

	}

	return targets;
}
