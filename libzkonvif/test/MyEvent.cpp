#include "MyEvent.h"
#include "../../common/utils.h"
#include "../../common/log.h"
#include "../../common/KVConfig.h"

MyEvent::MyEvent(int port)
{
	char buf[64];
	port_ = port;

	// 注意使用了 https !
	snprintf(buf, sizeof(buf), "https://%s:%d", util_get_myip(), port_);
	url_ = buf;

	start();
}

MyEvent::~MyEvent()
{
}

void MyEvent::run()
{
	KVConfig cfg("event.config");	// 事件服务配置 ..

#ifdef WITH_OPENSSL
	if (soap_ssl_server_context(soap, SOAP_SSL_DEFAULT, cfg.get_value("server-key", "server.pem"), 0, cfg.get_value("ca-cert", 0), 0, 0, 0, 0)) {
		log(LOG_FAULT, "%s: soap_ssl_server_context failure!\n", __func__);
		soap_print_fault(stderr);
		::exit(-1);
	}
#endif
	if (soap_valid_socket(this->soap->master) || soap_valid_socket(bind(NULL, port_, 100))) {
		for ( ; ; ) {
			if (!soap_valid_socket(accept())) {
				log(LOG_ERROR, "%s: soap_accept err??\n", __func__);
				continue;
			}

#ifdef WITH_OPENSSL
			if (soap_ssl_accept(soap)) {
				log(LOG_ERROR, "%s: soap_ssl_accept err???\n", __func__);
				soap_print_fault(stderr);
			}
			else {
				serve();
			}
#else
			serve();
#endif

			soap_destroy(this->soap);
			soap_end(this->soap);
		}
	}
}

int MyEvent::GetServiceCapabilities(_tev__GetServiceCapabilities *tev__GetServiceCapabilities,
									_tev__GetServiceCapabilitiesResponse *tev__GetServiceCapabilitiesResponse)
{
	tev__GetServiceCapabilitiesResponse->Capabilities = soap_new_tev__Capabilities(soap);

	// 不支持 basic notification interface .
	tev__GetServiceCapabilitiesResponse->Capabilities->MaxNotificationProducers = (int*)soap_malloc(soap, sizeof(int));
	*tev__GetServiceCapabilitiesResponse->Capabilities->MaxNotificationProducers = 0;

	// 不支持 seeking
	tev__GetServiceCapabilitiesResponse->Capabilities->PersistentNotificationStorage = (bool*)soap_malloc(soap, sizeof(bool));
	*tev__GetServiceCapabilitiesResponse->Capabilities->PersistentNotificationStorage = false;

	tev__GetServiceCapabilitiesResponse->Capabilities->MaxPullPoints = 0;

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
	/** 启动一个新的 socket，接收 PullMessageRequest, UnsubscribeRequest 等 */

	return SOAP_OK;
}
