#include "MyPtz.h"
#include <assert.h>
#include "../../common/log.h"

std::vector<tt__PTZConfiguration *> pConfigurations;
tt__PTZConfiguration* create_soap_tt__PTZConfiguration(struct soap *soap, tt__PTZConfiguration *tpc);
//
//	PTZ Configuration
//

int MyPtz::GetConfigurations(_tptz__GetConfigurations *tptz__GetConfigurations, _tptz__GetConfigurationsResponse *tptz__GetConfigurationsResponse)
{
	struct soap *sp = tptz__GetConfigurationsResponse->soap;
	std::vector<tt__PTZConfiguration *>::iterator c_it;
	tptz__GetConfigurationsResponse->PTZConfiguration.clear();
	for (c_it = pConfigurations.begin(); c_it != pConfigurations.end(); ++c_it) {
		tt__PTZConfiguration *pc = create_soap_tt__PTZConfiguration(tptz__GetConfigurationsResponse->soap, *c_it);
		tptz__GetConfigurationsResponse->PTZConfiguration.push_back(pc);
	}
	return SOAP_OK;
	
}

int MyPtz::SetConfiguration(_tptz__SetConfiguration *tptz__SetConfiguration, 
							_tptz__SetConfigurationResponse *tptz__SetConfigurationResponse)
{
	tt__PTZConfiguration *pPtzConfiguration = tptz__SetConfiguration->PTZConfiguration;
	tt__PTZConfiguration *pConfiguration = new tt__PTZConfiguration(*pPtzConfiguration);
	pConfiguration->NodeToken = pPtzConfiguration->NodeToken;

	if (pPtzConfiguration->DefaultAbsolutePantTiltPositionSpace != NULL)
		pConfiguration->DefaultAbsolutePantTiltPositionSpace = new std::string(*pPtzConfiguration->DefaultAbsolutePantTiltPositionSpace);

	if (pPtzConfiguration->DefaultAbsoluteZoomPositionSpace != NULL)
		pConfiguration->DefaultAbsoluteZoomPositionSpace = new std::string(*pPtzConfiguration->DefaultAbsoluteZoomPositionSpace);


	if (pPtzConfiguration->DefaultContinuousPanTiltVelocitySpace != NULL)
		pConfiguration->DefaultContinuousPanTiltVelocitySpace = new std::string(*pPtzConfiguration->DefaultContinuousPanTiltVelocitySpace);


	if (pPtzConfiguration->DefaultContinuousZoomVelocitySpace != NULL)
		pConfiguration->DefaultContinuousZoomVelocitySpace = new std::string(*pPtzConfiguration->DefaultContinuousZoomVelocitySpace);

	if (pPtzConfiguration->DefaultPTZSpeed != NULL) {
		pConfiguration->DefaultPTZSpeed = new tt__PTZSpeed(*pPtzConfiguration->DefaultPTZSpeed);
		if (pPtzConfiguration->DefaultPTZSpeed->PanTilt != NULL)
			pConfiguration->DefaultPTZSpeed->PanTilt = new tt__Vector2D(*pPtzConfiguration->DefaultPTZSpeed->PanTilt);
		if (pPtzConfiguration->DefaultPTZSpeed->Zoom != NULL)
			pConfiguration->DefaultPTZSpeed->Zoom = new tt__Vector1D(*pPtzConfiguration->DefaultPTZSpeed->Zoom);
	}

	if (pPtzConfiguration->DefaultPTZTimeout != NULL)
		pConfiguration->DefaultPTZTimeout = new (LONG64)(*pPtzConfiguration->DefaultPTZTimeout);

	if (pPtzConfiguration->DefaultRelativePanTiltTranslationSpace != NULL)
		pConfiguration->DefaultRelativePanTiltTranslationSpace = new std::string(*pPtzConfiguration->DefaultRelativePanTiltTranslationSpace);

	if (pPtzConfiguration->DefaultRelativeZoomTranslationSpace != NULL)
		pConfiguration->DefaultRelativeZoomTranslationSpace = new std::string(*pPtzConfiguration->DefaultRelativeZoomTranslationSpace);

	if (pPtzConfiguration->Extension != NULL) {
		//	TODO:
		;
	}
	
	if (pPtzConfiguration->PanTiltLimits != NULL) {
		//	TODO:
		;
	}

	pConfigurations.push_back(pConfiguration);

	return SOAP_OK;
}

int MyPtz::GetConfiguration(_tptz__GetConfiguration *tptz__GetConfiguration, _tptz__GetConfigurationResponse *tptz__GetConfigurationResponse)
{	
	std::vector<tt__PTZConfiguration *>::const_iterator c_it;
	for (c_it = pConfigurations.begin(); c_it != pConfigurations.end(); ++c_it) {
		if ((*c_it)->NodeToken == tptz__GetConfiguration->PTZConfigurationToken) {
			tptz__GetConfigurationResponse->PTZConfiguration = create_soap_tt__PTZConfiguration(tptz__GetConfigurationResponse->soap, *c_it);
			return SOAP_OK;
		}
	}

	return SOAP_ERR;	//	FIXME: ...
}

tt__PTZConfiguration* create_soap_tt__PTZConfiguration(struct soap *soap, tt__PTZConfiguration *tpc)
{
	tt__PTZConfiguration *pc = soap_new_tt__PTZConfiguration(soap);
	*pc = *tpc;

	if (tpc->DefaultAbsolutePantTiltPositionSpace != NULL) {
		pc->DefaultAbsolutePantTiltPositionSpace = soap_new_std__string(soap);
		*pc->DefaultAbsolutePantTiltPositionSpace = *tpc->DefaultAbsolutePantTiltPositionSpace;
	}
	if (tpc->DefaultAbsoluteZoomPositionSpace != NULL) {
		pc->DefaultAbsoluteZoomPositionSpace = soap_new_std__string(soap);
		*pc->DefaultAbsoluteZoomPositionSpace = *tpc->DefaultAbsoluteZoomPositionSpace;
	}
	if (tpc->DefaultContinuousPanTiltVelocitySpace != NULL) {
		pc->DefaultContinuousPanTiltVelocitySpace = soap_new_std__string(soap);
		*pc->DefaultContinuousPanTiltVelocitySpace = *tpc->DefaultContinuousPanTiltVelocitySpace;
	}
	// TODO: continue ...
	
	return pc;
}