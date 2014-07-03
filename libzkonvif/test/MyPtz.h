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
	//ptz Node
	virtual int GetNodes(_tptz__GetNodes *tptz__GetNodes, _tptz__GetNodesResponse *tptz__GetNodesResponse);
	virtual int GetNode(_tptz__GetNode *tptz__GetNode, _tptz__GetNodeResponse *tptz_GetNodeResponse);

	// PTZ Configuration
	virtual	int GetConfigurations(_tptz__GetConfigurations *tptz__GetConfigurations, _tptz__GetConfigurationsResponse *tptz__GetConfigurationsResponse);
	virtual	int SetConfiguration(_tptz__SetConfiguration *tptz__SetConfiguration, _tptz__SetConfigurationResponse *tptz__SetConfigurationResponse);
	virtual	int GetConfiguration(_tptz__GetConfiguration *tptz__GetConfiguration, _tptz__GetConfigurationResponse *tptz__GetConfigurationResponse);
	
	//PTZ Move
	virtual int RelativeMove(_tptz__RelativeMove *tptz__RelativeMove, _tptz__RelativeMoveResponse *tptz__RelativeMoveResponse);
	virtual int AbsoluteMove(_tptz__AbsoluteMove *tptz__AbsoluteMove, _tptz__AbsoluteMoveResponse *tptz__AbsoluteMoveResponse);
	virtual int GetStatus(_tptz__GetStatus *tptz__GetStatus, _tptz__GetStatusResponse *tptz_GetStatusResponse);
	virtual int Stop(_tptz__Stop *tptz__Stop, _tptz__StopResponse *tptz__StopResponse);

	//PTZ Preset
	virtual int GetPresets(_tptz__GetPresets *tptz__GetPresets, _tptz__GetPresetsResponse *tptz__GetPresetsResponse);
	virtual int SetPreset(_tptz__SetPreset *tptz__SetPreset, _tptz__SetPresetResponse *tptz__SetPresetResponse);
	virtual int GotoPreset(_tptz__GotoPreset *tptz__GotoPreset, _tptz__GotoPresetResponse *tptz__GotoPresetResponse);
	virtual int RemovePreset(_tptz__RemovePreset *tptz__RemovePreset, _tptz__RemovePresetResponse * tptz__RemovePresetResponse);

	//PTZ Other
	//setAbsolutionPosition();






};