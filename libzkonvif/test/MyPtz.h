#pragma once

#include "../soap/soapPTZBindingService.h"
#include <cc++/thread.h>
#include "myservice.inf.h"
#include "../../common/utils.h"

/** 云台接口
 */
class MyPtz : PTZBindingService
	, ost::Thread
	, public ServiceInf
{
	std::string url_;
	int port_;

public:
	MyPtz(int listen_port)
	{
		port_ = listen_port;

		char buf[128];
		snprintf(buf, sizeof(buf), "http://%s:%d", util_get_myip(), listen_port);

		url_ = buf;

		start();
	}

private:
	void run()
	{
		PTZBindingService::run(port_);
	}

	const char *url() const { return url_.c_str(); }
	const char *ns() const
	{
		// FIXME: 这里应该照着规矩来 ...
		return "ptz";
	}
	// PTZ Configuration
	virtual	int GetConfigurations(_tptz__GetConfigurations *tptz__GetConfigurations, _tptz__GetConfigurationsResponse *tptz__GetConfigurationsResponse);
	virtual	int SetConfiguration(const char *endpoint, const char *soap_action, _tptz__SetConfiguration *tptz__SetConfiguration, _tptz__SetConfigurationResponse *tptz__SetConfigurationResponse);
	virtual	int GetConfiguration(_tptz__GetConfiguration *tptz__GetConfiguration, _tptz__GetConfigurationResponse *tptz__GetConfigurationResponse)
};