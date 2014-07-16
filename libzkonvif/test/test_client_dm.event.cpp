#include "../soap/soapPullPointSubscriptionBindingProxy.h"
#include "../soap/wsseapi.h"
#include "../../common/log.h"
#include "../../common/utils.h"
#include "../../common/KVConfig.h"

// 测试事件 ...
void test_event(const tds__Service *service)
{
	int rc;
	fprintf(stdout, "\n\n%s: url=%s\n", __FUNCTION__, service->XAddr.c_str());

	PullPointSubscriptionBindingProxy pps, pps_p;	// pps 用于 CreatePullPointSubscription, pps_p 用于 PullMessage, ...

	// 使用 WS-usernameToken，参考 wsseapi.h 
	soap_wsse_add_UsernameTokenDigest(pps.soap, "id", "zonekey", "yekenoz");

#ifdef WITH_OPENSSL
	// 使用 tls ..
	KVConfig cfg("client.config");

	// ca-certs 的文件中，保存着签署 server 证书的 ca ...
	rc = soap_ssl_client_context(pps.soap, SOAP_SSL_DEFAULT | SOAP_SSL_SKIP_HOST_CHECK, 0, 0, cfg.get_value("cacerts", "cacerts.pem"), 0, 0);
	if (rc != SOAP_OK) {
		log(LOG_FAULT, "%s: soap_ssl_client_context faulure, code=%d, using cacerts='%s'\n", __func__, rc, cfg.get_value("cacerts", "cacerts.pem"));
		soap_print_fault(pps.soap, stderr);
		exit(-1);
	}

	log(LOG_DEBUG, "%s: soap_ssl_client_context ok, using cacerts='%s'\n", __func__, cfg.get_value("cacerts", "cacerts.pem"));
#endif

	{
		log(LOG_DEBUG, "===> try GetServiceCapabilities ...\n");

		/// GetServiceCapabilities
		_tev__GetServiceCapabilities req;
		_tev__GetServiceCapabilitiesResponse res;
		rc = pps.GetServiceCapabilities(service->XAddr.c_str(), 0, &req, &res);
		if (rc != SOAP_OK) {
			log(LOG_ERROR, "%s: GetServiceCapablities err, code=%d\n", __func__, rc);
			soap_print_fault(pps.soap, stderr);
		}
		else {
			log(LOG_DEBUG, "%s: GetServiceCapablities ok\n", __func__);
		}
	}

	{
		log(LOG_DEBUG, "===> try CreatePullPointSubscription ...\n");

		/// CreatePullPointSubscription
		_tev__CreatePullPointSubscription req;
		_tev__CreatePullPointSubscriptionResponse res;

		rc = pps.CreatePullPointSubscription(service->XAddr.c_str(), 0, &req, &res);
		if (rc != SOAP_OK) {
			log(LOG_ERROR, "%s: CreatePullPointSubscription err, code=%d\n", __func__, rc);
			soap_print_fault(pps.soap, stderr);
		}
		else {
			log(LOG_DEBUG, "%s: CreatePullPointSubscription ok\n", __func__);

			struct tm *ptm = localtime(&res.wsnt__CurrentTime);
			log(LOG_DEBUG, "\t CurrentTime=%04d-%02d-%02d %02d:%02d:%02d\n",
				ptm->tm_year + 1900, ptm->tm_min + 1, ptm->tm_mday,
				ptm->tm_hour, ptm->tm_min, ptm->tm_sec);

			ptm = localtime(&res.wsnt__TerminationTime);
			log(LOG_DEBUG, "\t TerminateTime=%04d-%02d-%02d %02d:%02d:%02d\n",
				ptm->tm_year + 1900, ptm->tm_min + 1, ptm->tm_mday,
				ptm->tm_hour, ptm->tm_min, ptm->tm_sec);

			log(LOG_DEBUG, "\t pullpoint url='%s'\n", res.SubscriptionReference.Address);

			const char *endpoint = res.SubscriptionReference.Address;
			{
				log(LOG_DEBUG, "===> try PullMessage ...\n");

				/// PullMessage
				_tev__PullMessages req;
				_tev__PullMessagesResponse res;

				req.MessageLimit = 0;
				req.Timeout = 10;	// 10 秒超时 ??? .

				rc = pps_p.PullMessages(endpoint, 0, &req, &res);
				if (rc != SOAP_OK) {
					log(LOG_ERROR, "%s: PullMessage for '%s' err, code=%d\n", __func__, endpoint, rc);
				}
				else {
					log(LOG_DEBUG, "%s: PullMessage for '%s' ok\n", __func__, endpoint);
					log(LOG_DEBUG, "\t en there are %u messages\n", res.wsnt__NotificationMessage.size());
					std::vector<class wsnt__NotificationMessageHolderType * >::const_iterator it;
					for (it = res.wsnt__NotificationMessage.begin(); it != res.wsnt__NotificationMessage.end(); ++it) {
						log(LOG_DEBUG, "\t\t: %s/%s: code=%d, info=%s\n", (*it)->Message.Message->ns.c_str(),
							(*it)->Message.Message->sid.c_str(), (int)(*it)->Message.Message->code, (*it)->Message.Message->info.c_str());
					}
				}
			}

			{
				log(LOG_DEBUG, "===> try Unsubscribe ...\n");

				/// UnSubscribe
				_wsnt__Unsubscribe req;
				_wsnt__UnsubscribeResponse res;

				rc = pps_p.Unsubscribe(endpoint, 0, &req, &res);
				if (rc != SOAP_OK) {
					log(LOG_ERROR, "%s: Unsubecribe for '%s' err, code=%d\n", __func__, endpoint, rc);
				}
				else {
					log(LOG_DEBUG, "%s: Unsubscribe for '%s' ok\n", __func__, endpoint);
				}
			}
		}
	}

	log(LOG_INFO, "%s: end \n\n", __func__);
}
