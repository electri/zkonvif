#pragma once

#include <cc++/thread.h>
#include "../soap/soapwsddService.h"
#include "MyDevice.h"
/** 设备发现, 声明 MyDevice 接口
 */
class MyDeviceDiscovery : wsddService
	, ost::Thread
{
	const MyDevice *device_;

public:
	MyDeviceDiscovery(const MyDevice *device) : wsddService(SOAP_IO_UDP)	// 总是 udp 模式
	{
		device_ = device;

		start();	// 启动工作线程 .
	}

private:
	void run();

private:
	static const char *my_messageid()
	{
		static int _i = 0;
		static char buf[64];

		snprintf(buf, sizeof(buf), "id:%u", _i++);

		return buf;
	}

	virtual int Probe(struct wsdd__ProbeType *probe);

	static int debug_before_send(struct soap *soap, const char *data, size_t len);

	/** 下面这段代码从 soapwsddProxy.cpp 中复制的, 稍加修改 :)
	  * 声明为 static 的目的是防止使用 members
	 */
	static int __send_ProbeMatches(struct soap *soap, const char *soap_endpoint, const char *soap_action, struct wsdd__ProbeMatchesType *wsdd__ProbeMatches);

};