#include "../soap/soapPTZBindingProxy.h"
#ifdef WITH_OPENSSL
#	include "../soap/wsseapi.h"
#endif
#include "../../common/log.h"
#include "../../common/utils.h"
#include "../../common/KVConfig.h"
//#include "../soap/stdsoap2.h"

// 测试云台 ...
void test_ptz(const zonekey__ZonekeyDMServiceType *service)
{
	int rc;
	PTZBindingProxy ptz;
	fprintf(stdout, "%s: url=%s\n", __FUNCTION__, service->url.c_str());

#ifdef WITH_OPENSSL
	//使用 WS-usernameToken, 参考 wsseapi.h
	soap_wsse_add_UsernameTokenDigest(ptz.soap, "id", "zonekey", "yekenoz");

	// 使用tls ..
	KVConfig cfg("client.config");

	//ca-certs 的文件中,保存着签署 server 证书的 ca ...
	rc = soap_ssl_client_context(ptz.soap, SOAP_SSL_DEFAULT | SOAP_SSL_SKIP_HOST_CHECK, 0, 0, cfg.get_value("cacerts", "cacerts.pem"), 0, 0);
	if (rc != SOAP_OK) {
		log(LOG_FAULT, "%s: soap_ssl_client_context faulure, code = %d, using cacerts = %s\n", __func__, rc, cfg.get_value("cacerts", "cacerts.pem"));
		soap_print_fault(ptz.soap, stderr);
		exit(-1);
	}

	log(LOG_DEBUG, "%s: soap_ssl_client_context ok, using cacerts='%s'\n", __func__, cfg.get_value("cacerts", "cacerts.pem"));

	_tptz__GetServiceCapabilities req;
	_tptz__GetServiceCapabilitiesResponse res;
	rc = ptz.GetServiceCapabilities(service->url.c_str(), 0, &req, &res);
	if (rc != SOAP_OK) {
		log(LOG_ERROR, "%S: GetServiceCapabilities err, code = %d\n", __func__, rc);
		soap_print_fault(ptz.soap, stderr);
	}
	else {
		log(LOG_DEBUG, "%s: GetServiceCapabilities ok\n", __func__);
	}


#endif
}

void test_ptz_GetConfigurations(PTZBindingProxy *ptz, const zonekey__ZonekeyDMServiceType *service)
{
	int rc;

	log(LOG_DEBUG, "===> try CreatePullPointSubscription ...\n");

	_tptz__GetConfigurations req;
	_tptz__GetConfigurationsResponse res;

	rc = ptz->GetConfigurations(service->url.c_str(), 0, &req, &res);
	if (rc != SOAP_OK) {
		log(LOG_ERROR, "%s: PTZ GetConfigurations err, code = %d\n", __func__, rc);
		soap_print_fault(ptz->soap, stderr);
	}
	else {
		log(LOG_DEBUG, "%s: PTZ GetConfiguration ok\n", __func__);

		std::vector<tt__PTZConfiguration *> v_pc = res.PTZConfiguration;

		std::vector<tt__PTZConfiguration *>::const_iterator it;
		for (it = v_pc.begin(); it != v_pc.end(); ++it) {
			fprintf(stderr, "NodeToken = %s\n", (*it)->NodeToken.c_str());
			if ((*it)->DefaultAbsolutePantTiltPositionSpace != NULL)
				fprintf(stderr, "DefaultAbsolutePantTiltPositionSpace = %s\n", (*it)->DefaultAbsolutePantTiltPositionSpace->c_str());
			if ((*it)->DefaultAbsoluteZoomPositionSpace != NULL)
				fprintf(stderr, "DefualtAbsoluteZoomPostionSpace  = %s \n", (*it)->DefaultAbsoluteZoomPositionSpace->c_str());
		}
	}

	log(LOG_DEBUG, "%s end \n\n", __func__);
}

void test_ptz_SetConfiguration(PTZBindingProxy *ptz, const zonekey__ZonekeyDMServiceType *service, _tptz__SetConfiguration *req)
{
	int rc;

	log(LOG_DEBUG, "===> try SetConfiguration ...\n");

	_tptz__SetConfigurationResponse res;
	rc = ptz->SetConfiguration(service->url.c_str(), 0, req, &res);

	if (rc != SOAP_OK) {
		log(LOG_ERROR, "%s: PTZ SetConfiguration err, code = %d\n", __func__, rc);
		soap_print_fault(ptz->soap, stderr);
	}
	else {
		log(LOG_DEBUG, "%s: PTZ SetConfiguration ok\n", __func__);
	}
}

void test_ptz_GetConfiguration(PTZBindingProxy *ptz, const zonekey__ZonekeyDMServiceType *service, _tptz__GetConfiguration *req, _tptz__GetConfigurationResponse *res)
{
	int rc;
	log(LOG_DEBUG, "===> try GetConfiguration ...\n");
	
	rc = ptz->GetConfiguration(service->url.c_str(), 0, req, res);

	if (rc != SOAP_OK) {
		log(LOG_ERROR, "%s: PTZ GetConfiguration err, code = %d\n", __func__, rc);
		soap_print_fault(ptz->soap, stderr);
	}
	else {
		log(LOG_DEBUG, "%s: PTZ SetConfiguration ok\n", __func__);
	}
}
