#include "MyEvent.h"
#include "../../common/utils.h"
#include "../../common/log.h"

MyEvent::MyEvent(int port)
{
	port_ = port;

	char buf[64];
	snprintf(buf, sizeof(buf), "http://%s:%d", util_get_myip(), port_);
	url_ = buf;

	start();
}

MyEvent::~MyEvent()
{
}

void MyEvent::run()
{
	PullPointSubscriptionBindingService::run(port_);
}
