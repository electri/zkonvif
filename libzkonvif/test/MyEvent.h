/** 实现 event 接口 */

#pragma once
#include "../soap/soapPullPointSubscriptionBindingService.h"
#include "myservice.inf.h"
#include <cc++/thread.h>
#include <vector>
#include <string>

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
};
