#include "MyPtz.h"
#include <assert.h>
#include "../../common/log.h"

//
//	PTZ Configuration
//

int MyPtz::GetConfigurations(_tptz__GetConfigurations *tptz__GetConfigurations, _tptz__GetConfigurationsResponse *tptz__GetConfigurationsResponse)
{
	std::vector<tt__PTZConfiguration * > &configs = tptz__GetConfigurationsResponse->PTZConfiguration;
	
}

