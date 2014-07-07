#include "MyPtz.h"
#include <assert.h>
#include "../../common/log.h"
#include "../../common/utils.h"
#include "PtzControling.h"
#include <map>

typedef std::pair<std::string, PtzControlling *> ptz_pair;
std::map<std::string,PtzControlling*> ptzes;

std::vector<tt__PTZConfiguration *> pConfigurations;

tt__PTZConfiguration* new_soap_tt__PTZConfiguration(struct soap *soap, tt__PTZConfiguration *tpc);

void delete_tt__PTZConfigurations(std::vector<tt__PTZConfiguration *> pConfigurations);

MyPtz::MyPtz(int listen_port)
{
	port_ = listen_port;

	char buf[128];
	snprintf(buf, sizeof(buf), "http://%s:%d", util_get_myip(), listen_port);

	url_ = buf;

	start();

	//
	// 打开 所有云台节点
	//
	KVConfig ptzKVC("../config/ptz_nodes");
	std::vector<std::string> tokenList = ptzKVC.keys();
	std::vector<std::string>::const_iterator c_it;
	for (c_it = tokenList.begin(); c_it != tokenList.end(); ++c_it) {
		//为返回值 赋值
		const char *value = ptzKVC.get_value(c_it->c_str(), "teacher");
		char name[255] = "\0";
		_snprintf(name, 255, "../config/%s", value);

		// 创建 ptz, 保存至 ptz 列表
		KVConfig comKVC(name);
		PtzControlling * ptzVisca = new PtzControllingVisca(&comKVC);
		ptzes.insert(ptz_pair(*c_it, ptzVisca));
		ptzVisca->open();
	}
}

//
//ptz Node
//
int MyPtz::GetNodes(_tptz__GetNodes *tptz__GetNodes, _tptz__GetNodesResponse *tptz__GetNodesResponse)
{
	struct soap *pSoap = tptz__GetNodesResponse->soap;

	KVConfig ptzKVC("../config/ptz_nodes");
	std::vector<std::string> tokenList = ptzKVC.keys();
	

	std::vector<std::string>::const_iterator c_it;
	for (c_it = tokenList.begin(); c_it != tokenList.end(); ++c_it) {
		tt__PTZNode *ptzNode = soap_new_tt__PTZNode(pSoap);
		ptzNode->token = *c_it;
		std::string *pName = soap_new_std__string(soap);

		const char *value = ptzKVC.get_value(c_it->c_str());
		pName->assign(value, strlen(value));
		ptzNode->Name = pName;
		ptzNode->Extension = NULL;
		ptzNode->FixedHomePosition = 0;
		ptzNode->HomeSupported = true;
		ptzNode->MaximumNumberOfPresets = 4;
		tptz__GetNodesResponse->PTZNode.push_back(ptzNode);
	}

	return SOAP_OK;
}

int MyPtz::GetNode(_tptz__GetNode *tptz__GetNode, _tptz__GetNodeResponse *tptz__GetNodeResponse)
{
	//TODO:
	struct soap *pSoap = tptz__GetNodeResponse->soap;

	KVConfig ptzKVC("../config/ptz_nodes");
	std::vector<std::string> tokenList = ptzKVC.keys();

	std::vector<std::string>::const_iterator c_it;

	//是否存在相匹配云台节点
	for (c_it = tokenList.begin(); c_it != tokenList.end(); ++c_it) {
		if (*c_it == tptz__GetNode->NodeToken) {
			tt__PTZNode *ptzNode = soap_new_tt__PTZNode(pSoap);
			ptzNode->token = *c_it;
			std::string *pName = soap_new_std__string(soap);
			
			//为返回值 赋值
			const char *value = ptzKVC.get_value(c_it->c_str(), "teacher");
			pName->assign(value, strlen(value));
			ptzNode->Name = pName;
			ptzNode->Extension = NULL;
			ptzNode->FixedHomePosition = 0;
			ptzNode->HomeSupported = true;
			ptzNode->MaximumNumberOfPresets = 4;
			tptz__GetNodeResponse->PTZNode = ptzNode;

			char name[255] = "\0";
			_snprintf(name, 255, "../config/%s", value);

			// 创建 ptz, 保存至 ptz 列表
			KVConfig comKVC(name);
			PtzControlling * ptzVisca = new PtzControllingVisca(&comKVC);
			ptzes.insert(ptz_pair(*c_it, ptzVisca));
			ptzVisca->open();
			return SOAP_OK;
		}
	}

	return SOAP_ERR;
}
//
//	PTZ Configuration
//

int MyPtz::GetConfigurations(_tptz__GetConfigurations *tptz__GetConfigurations, _tptz__GetConfigurationsResponse *tptz__GetConfigurationsResponse)
{
	struct soap *sp = tptz__GetConfigurationsResponse->soap;
	std::vector<tt__PTZConfiguration *>::iterator c_it;
	tptz__GetConfigurationsResponse->PTZConfiguration.clear();
	for (c_it = pConfigurations.begin(); c_it != pConfigurations.end(); ++c_it) {
		tt__PTZConfiguration *pc = new_soap_tt__PTZConfiguration(tptz__GetConfigurationsResponse->soap, *c_it);
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
			tptz__GetConfigurationResponse->PTZConfiguration = new_soap_tt__PTZConfiguration(tptz__GetConfigurationResponse->soap, *c_it);
			return SOAP_OK;
		}
	}

	return SOAP_ERR;	//	FIXME: ...
}

//
//PTZ Move
//
int MyPtz::RelativeMove(_tptz__RelativeMove *tptz__RelativeMove, _tptz__RelativeMoveResponse *tptz__RelativeMoveResponse)
{
	//TODO:
	return SOAP_OK;
}

int MyPtz::AbsoluteMove(_tptz__AbsoluteMove *tptz__AbsoluteMove, _tptz__AbsoluteMoveResponse *tptz__AbsoluteMoveResponse)
{
	std::string key = tptz__AbsoluteMove->ProfileToken;

	int speedx = 32;
	int speedy = 32;
	int speedz = 7;

	if (tptz__AbsoluteMove->Speed) {
		if (tptz__AbsoluteMove->Speed->PanTilt) {
			speedx = tptz__AbsoluteMove->Speed->PanTilt->x;
			speedy = tptz__AbsoluteMove->Speed->PanTilt->y;
		}
		if (tptz__AbsoluteMove->Speed->Zoom)
			speedz = tptz__AbsoluteMove->Speed->Zoom->x;
	}

	if (tptz__AbsoluteMove->Position) {
		if (tptz__AbsoluteMove->Position->PanTilt) {
			int x = tptz__AbsoluteMove->Position->PanTilt->x;
			int y = tptz__AbsoluteMove->Position->PanTilt->y;
			ptzes[key]->setpos(x, y, speedx, speedy);
		}

		if (tptz__AbsoluteMove->Position->Zoom) {
			ptzes[key]->zoom_set(speedz);
		}
	}

	return SOAP_OK;
}

int MyPtz::ContinuousMove(_tptz__ContinuousMove *tptz__ContinuousMove, _tptz__ContinuousMoveResponse *tptz__ContinuousMoveResponse)
{
	std::string key = tptz__ContinuousMove->ProfileToken;

	int speedx = 32;
	int speedy = 32;
	
	if (tptz__ContinuousMove->Velocity->PanTilt) {
		speedx = tptz__ContinuousMove->Velocity->PanTilt->x;
		speedy = tptz__ContinuousMove->Velocity->PanTilt->y;
	}

	if (speedx < 0)
		ptzes[key]->left(-speedx);
	if (speedx > 0)
		ptzes[key]->right(speedx);

	if (speedy > 0)
		ptzes[key]->up(speedy);
	if (speedy < 0)
		ptzes[key]->down(-speedy);

	if (tptz__ContinuousMove->Velocity->Zoom) {
		float speedz = tptz__ContinuousMove->Velocity->Zoom->x;
		ptzes[key]->zoom_set(speedz);
	}
	

	return SOAP_OK;	
}

int MyPtz::GetStatus(_tptz__GetStatus *tptz__GetStatus, _tptz__GetStatusResponse *tptz_GetStatusResponse)
{
	//TODO:
	std::string key = tptz__GetStatus->ProfileToken;
	struct soap *pSoap = tptz_GetStatusResponse->soap;

	tt__PTZStatus * ptzStatus = soap_new_tt__PTZStatus(soap);

	tt__PTZVector *position = soap_new_tt__PTZVector(soap);

	tt__Vector2D *panTilt = soap_new_tt__Vector2D(soap);

	int x, y;
	ptzes[key]->getpos(x, y); 
	panTilt->x = x, panTilt->y = y;
	
	position->PanTilt = panTilt;

	int z;
	position->Zoom = soap_new_tt__Vector1D(soap);
	ptzes[key]->zoom_get(z);
	position->Zoom->x = z;

	ptzStatus->Position = position;
	ptzStatus->Error = NULL;
	ptzStatus->MoveStatus = NULL;
	//ptzStatus->UtcTime =

	tptz_GetStatusResponse->PTZStatus = ptzStatus;
	return SOAP_OK;
}

int MyPtz::Stop(_tptz__Stop *tptz__Stop, _tptz__StopResponse *tptz__StopResponse)
{
	std::string key = tptz__Stop->ProfileToken;

	ptzes[key]->stop();
	return SOAP_OK;
}

//
//PTZ Preset
//

int MyPtz::GetPresets(_tptz__GetPresets *tptz__GetPresets, _tptz__GetPresetsResponse *tptz__GetPresetsResponse)
{
	//TODO:
	return SOAP_OK;
}

int MyPtz::SetPreset(_tptz__SetPreset *tptz__SetPreset, _tptz__SetPresetResponse *tptz__SetPresetResponse)
{
	//TODO:
	return SOAP_OK;
}

int MyPtz::GotoPreset(_tptz__GotoPreset *tptz__GotoPreset, _tptz__GotoPresetResponse *tptz__GotoPresetResponse)
{
	//TODO:
	return SOAP_OK;
}

int MyPtz::RemovePreset(_tptz__RemovePreset *tptz__RemovePreset, _tptz__RemovePresetResponse * tptz__RemovePresetResponse)
{
	//.TODO:
	return SOAP_OK;
}

tt__PTZConfiguration* new_soap_tt__PTZConfiguration(struct soap *soap, tt__PTZConfiguration *tpc)
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

void delete_tt__PTZConfigurations(std::vector<tt__PTZConfiguration *> pConfigurations)
{
	//TODO:当关机时,需要释放掉 configurations
}

MyPtz::~MyPtz()
{
	std::map<std::string, PtzControlling *>::const_iterator c_it;
	for (c_it = ptzes.begin(); c_it != ptzes.end(); ++c_it) {
		c_it->second->close();
		delete(c_it->second);
	}
}

