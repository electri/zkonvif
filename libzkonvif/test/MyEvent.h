/** 实现 event 接口 */

#pragma once
#include "../soap/soapPullPointSubscriptionBindingService.h"
#include "myservice.inf.h"
#include <cc++/thread.h>
#include <vector>
#include <string>

/** 实现 Real-time Pull-Point Notification Interface 模型  (core 9.2)  */
class MyEvent : PullPointSubscriptionBindingService
			  , ost::Thread
			  , public ServiceInf
{
	int port_;
	std::string url_;

public:
	MyEvent(int port);
	virtual ~MyEvent();

private:
	const char *url() const { return url_.c_str(); }
	void run();

private:
	virtual	int GetServiceCapabilities(_tev__GetServiceCapabilities *tev__GetServiceCapabilities,
									   _tev__GetServiceCapabilitiesResponse *tev__GetServiceCapabilitiesResponse);

	virtual	int GetEventProperties(_tev__GetEventProperties *tev__GetEventProperties, 
								   _tev__GetEventPropertiesResponse *tev__GetEventPropertiesResponse);

	virtual	int CreatePullPointSubscription(_tev__CreatePullPointSubscription *tev__CreatePullPointSubscription,
											_tev__CreatePullPointSubscriptionResponse *tev__CreatePullPointSubscriptionResponse);
};
