#include "MyPtz.h"
#include <assert.h>
#include "../../common/log.h"

std::vector<tt__PTZConfiguration * > configurations;

//
//	PTZ Configuration
//

int MyPtz::GetConfigurations(_tptz__GetConfigurations *tptz__GetConfigurations, _tptz__GetConfigurationsResponse *tptz__GetConfigurationsResponse)
{
	std::vector<tt__PTZConfiguration * > &configs = tptz__GetConfigurationsResponse->PTZConfiguration;

	return 0;
	
}

int MyPtz::SetConfiguration(const char *endpoint, const char *soap_action, _tptz__SetConfiguration *tptz__SetConfiguration, _tptz__SetConfigurationResponse *tptz__SetConfigurationResponse)
{
	tt__PTZConfiguration *pconfiguration = new tt__PTZConfiguration();
	pconfiguration->NodeToken = tptz__SetConfiguration->PTZConfiguration->NodeToken;
	pconfiguration->DefaultAbsolutePantTiltPositionSpace = NULL;
	pconfiguration->DefaultAbsoluteZoomPositionSpace = NULL;
	pconfiguration->DefaultContinuousPanTiltVelocitySpace = NULL;
	pconfiguration->DefaultContinuousZoomVelocitySpace = NULL;
	pconfiguration->DefaultPTZSpeed = NULL;
	pconfiguration->DefaultPTZTimeout = NULL; //	FIXME: .
	pconfiguration->DefaultRelativePanTiltTranslationSpace = 0;
	return 0;
}