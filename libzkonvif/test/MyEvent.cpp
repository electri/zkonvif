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

int MyEvent::GetServiceCapabilities(_tev__GetServiceCapabilities *tev__GetServiceCapabilities,
									_tev__GetServiceCapabilitiesResponse *tev__GetServiceCapabilitiesResponse)
{
	tev__GetServiceCapabilitiesResponse->Capabilities = (tev__Capabilities*)soap_malloc(soap, sizeof(tev__Capabilities));
	memset(&tev__GetServiceCapabilitiesResponse->Capabilities, 0, sizeof(tev__Capabilities));

	// 不支持 basic notification interface .
	tev__GetServiceCapabilitiesResponse->Capabilities->MaxNotificationProducers = (int*)soap_malloc(soap, sizeof(int));
	*tev__GetServiceCapabilitiesResponse->Capabilities->MaxNotificationProducers = 0;

	// 不支持 seeking
	tev__GetServiceCapabilitiesResponse->Capabilities->PersistentNotificationStorage = (bool*)soap_malloc(soap, sizeof(bool));
	*tev__GetServiceCapabilitiesResponse->Capabilities->PersistentNotificationStorage = false;



	return SOAP_OK;
}

int MyEvent::GetEventProperties(_tev__GetEventProperties *tev__GetEventProperties,
								_tev__GetEventPropertiesResponse *tev__GetEventPropertiesResponse)
{
	return SOAP_OK;
}

int MyEvent::CreatePullPointSubscription(_tev__CreatePullPointSubscription *tev__CreatePullPointSubscription,
										 _tev__CreatePullPointSubscriptionResponse *tev__CreatePullPointSubscriptionResponse)
{
	return SOAP_OK;
}
