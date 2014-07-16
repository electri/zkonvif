#include "MyPtz.h"
#include <assert.h>
#include "../../common/log.h"
#include "../../common/utils.h"
#include "PtzControling.h"
#include <map>
#include <algorithm>

typedef std::pair<std::string, PtzControlling *> ptz_pair;
static std::map<std::string,PtzControlling*> _ptzes;
static KVConfig *_ptzKVC;

void set_SOAP_ENV__Fault(soap *soap, char *env, char *ter0, char *ter1, char *text);

MyPtz::MyPtz(int listen_port)
{
	port_ = listen_port;

	char buf[128];
	snprintf(buf, sizeof(buf), "http://%s:%d", util_get_myip(), listen_port);

	url_ = buf;

	//
	// 打开 所有云台节点. 
	//
	_ptzKVC = new KVConfig("config/ptz_nodes");
	std::vector<std::string> tokenList = _ptzKVC->keys();
	std::vector<std::string>::const_iterator c_it;
	for (c_it = tokenList.begin(); c_it != tokenList.end(); ++c_it) {
		//为返回值 赋值. 
		const char *value = _ptzKVC->get_value(c_it->c_str(), "teacher");
		char name[255] = "\0";
		snprintf(name, 255, "config/%s", value);

		// 创建 ptz, 保存至 ptz 列表. 
		KVConfig *comKVC = new KVConfig(name);
		PtzControlling * ptzVisca = new PtzControllingVisca(comKVC);
		//ptzes.insert(ptz_pair(*c_it, ptzVisca));
		_ptzes[*c_it] = ptzVisca;
		ptzVisca->open();
	}

	start();
}

//
//ptz Node
//
int MyPtz::GetNodes(_tptz__GetNodes *tptz__GetNodes, _tptz__GetNodesResponse *tptz__GetNodesResponse)
{
	struct soap *pSoap = tptz__GetNodesResponse->soap;

	std::vector<std::string> tokenList = _ptzKVC->keys();
	
	std::vector<std::string>::const_iterator c_it;
	for (c_it = tokenList.begin(); c_it != tokenList.end(); ++c_it) {
		tt__PTZNode *ptzNode = soap_new_tt__PTZNode(pSoap);
		ptzNode->token = *c_it;
		std::string *pName = soap_new_std__string(soap);

		const char *value = _ptzKVC->get_value(c_it->c_str());
		pName->assign(value, strlen(value));
		ptzNode->Name = pName;
		ptzNode->Extension = NULL;
		ptzNode->FixedHomePosition = 0;
		ptzNode->HomeSupported = true;
		ptzNode->MaximumNumberOfPresets = 4;
		tptz__GetNodesResponse->PTZNode.push_back(ptzNode);
	}

	if (tokenList.size() == 0) {
		
		soap_print_fault(stderr);
		set_SOAP_ENV__Fault(soap, "env:Receiver", "ter:ActionNotSupported", "ter:PTZNotSupported", "PTZ is not supported by the device");
		return SOAP_ERR;
	}

	return SOAP_OK;
}

int MyPtz::GetNode(_tptz__GetNode *tptz__GetNode, _tptz__GetNodeResponse *tptz__GetNodeResponse)
{
	//TODO:
	struct soap *pSoap = tptz__GetNodeResponse->soap;

	std::vector<std::string> tokenList = _ptzKVC->keys();

	std::vector<std::string>::const_iterator c_it;

	//是否存在相匹配云台节点. 
	for (c_it = tokenList.begin(); c_it != tokenList.end(); ++c_it) {
		if (*c_it == tptz__GetNode->NodeToken) {
			tt__PTZNode *ptzNode = soap_new_tt__PTZNode(pSoap);
			ptzNode->token = *c_it;
			std::string *pName = soap_new_std__string(soap);
			
			//为返回值 赋值. 
			const char *value = _ptzKVC->get_value(c_it->c_str(), "teacher");
			pName->assign(value, strlen(value));
			ptzNode->Name = pName;
			ptzNode->Extension = NULL;
			ptzNode->FixedHomePosition = 0;
			ptzNode->HomeSupported = true;
			ptzNode->MaximumNumberOfPresets = 4;
			tptz__GetNodeResponse->PTZNode = ptzNode;

			return SOAP_OK;
		}
	}
	soap_print_fault(stderr);
	set_SOAP_ENV__Fault(soap, "env:Sender", "ter:InvalidArgVal", "ter:NoEntity", "No such PTZNode on the device");

	return SOAP_ERR;
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
	std::vector<std::string> tokenList = _ptzKVC->keys();
	
	if (std::find(tokenList.begin(), tokenList.end(), key) == tokenList.end()) {
		soap_print_fault(stderr);
		set_SOAP_ENV__Fault(soap, "env:Sender", "ter:InvalidArgVal", "ter:NoEntity", "the requested profile token ProfileToken does not exist");
		
		return SOAP_ERR;
	}

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
			_ptzes[key]->setpos(x, y, speedx, speedy);
		}

		if (tptz__AbsoluteMove->Position->Zoom) {
			_ptzes[key]->zoom_set(speedz);
		}
	}

	return SOAP_OK;
}

int MyPtz::ContinuousMove(_tptz__ContinuousMove *tptz__ContinuousMove, _tptz__ContinuousMoveResponse *tptz__ContinuousMoveResponse)
{
	
	std::string key = tptz__ContinuousMove->ProfileToken;

	std::vector<std::string> tokenList = _ptzKVC->keys();


	if (std::find(tokenList.begin(), tokenList.end(), key) == tokenList.end()) {
		soap_print_fault(stderr);
		set_SOAP_ENV__Fault(soap, "env:Sender", "ter:InvalidArgVal", "ter:NoEntity", "the requested profile token ProfileToken does not exist");
		
		return SOAP_ERR;
	}

	int speedx = 32;
	int speedy = 32;
	
	if (tptz__ContinuousMove->Velocity->PanTilt) {
		speedx = tptz__ContinuousMove->Velocity->PanTilt->x;
		speedy = tptz__ContinuousMove->Velocity->PanTilt->y;
	}

	if (speedx < 0)
		_ptzes[key]->left(-speedx);
	if (speedx > 0)
		_ptzes[key]->right(speedx);

	if (speedy > 0)
		_ptzes[key]->up(speedy);
	if (speedy < 0)
		_ptzes[key]->down(-speedy);
	
	return SOAP_OK;	
}

int MyPtz::GetStatus(_tptz__GetStatus *tptz__GetStatus, _tptz__GetStatusResponse *tptz_GetStatusResponse)
{
	//TODO:
	std::string key = tptz__GetStatus->ProfileToken;
	std::vector<std::string> tokenList = _ptzKVC->keys();

	if (std::find(tokenList.begin(), tokenList.end(), key) == tokenList.end()) {
		soap_print_fault(stderr);
		set_SOAP_ENV__Fault(soap, "env:Sender", "ter:InvalidArgVal", "ter:NoEntity", "the requested profile token ProfileToken does not exist");

		return SOAP_ERR;
	}
	struct soap *pSoap = tptz_GetStatusResponse->soap;

	tt__PTZStatus * ptzStatus = soap_new_tt__PTZStatus(soap);

	tt__PTZVector *position = soap_new_tt__PTZVector(soap);

	tt__Vector2D *panTilt = soap_new_tt__Vector2D(soap);

	int x, y;
	_ptzes[key]->getpos(x, y); 
	panTilt->x = x, panTilt->y = y;
	
	position->PanTilt = panTilt;

	int z;
	position->Zoom = soap_new_tt__Vector1D(soap);
	_ptzes[key]->zoom_get(z);
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
	std::vector<std::string> tokenList = _ptzKVC->keys();

	if (std::find(tokenList.begin(), tokenList.end(), key) == tokenList.end()) {
		soap_print_fault(stderr);
		set_SOAP_ENV__Fault(soap, "env:Sender", "ter:InvalidArgVal", "ter:NoEntity", "the requested profile token ProfileToken does not exist");

		return SOAP_ERR;
	}

	_ptzes[key]->stop();
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
	std::string key = tptz__SetPreset->ProfileToken;
	std::vector<std::string> tokenList = _ptzKVC->keys();

	if (std::find(tokenList.begin(), tokenList.end(), key) == tokenList.end()) {
		soap_print_fault(stderr);
		set_SOAP_ENV__Fault(soap, "env:Sender", "ter:InvalidArgVal", "ter:NoEntity", "the requested profile token ProfileToken does not exist");

		return SOAP_ERR;
	}
	else {
		if (tptz__SetPreset->PresetToken == NULL) {
			soap_print_fault(stderr);
			set_SOAP_ENV__Fault(soap, "env:Sender", "ter:InvalidArgVal", "ter:NoProfile", "The requested preset profile token ProfileToken does not exist");

			return SOAP_ERR;
		}
		_ptzes[key]->preset_set(atoi(tptz__SetPreset->PresetToken->c_str()));
		tptz__SetPresetResponse->PresetToken = *tptz__SetPreset->PresetToken;
	}
	return SOAP_OK;
}

int MyPtz::GotoPreset(_tptz__GotoPreset *tptz__GotoPreset, _tptz__GotoPresetResponse *tptz__GotoPresetResponse)
{
	struct soap *soap = tptz__GotoPresetResponse->soap;
	std::string key = tptz__GotoPreset->ProfileToken;
	std::vector<std::string> tokenList = _ptzKVC->keys();
	
	if (std::find(tokenList.begin(), tokenList.end(), key) == tokenList.end()) {
		soap_print_fault(stderr);
		set_SOAP_ENV__Fault(soap, "env:Sender", "ter:InvalidArgVal", "ter:NoEntity", "the requested profile token ProfileToken does not exist");

		return SOAP_ERR;
	}
	else {
		_ptzes[key]->preset_get(atoi(tptz__GotoPreset->PresetToken.c_str()));
	}

	return SOAP_OK;
}

int MyPtz::RemovePreset(_tptz__RemovePreset *tptz__RemovePreset, _tptz__RemovePresetResponse * tptz__RemovePresetResponse)
{
	std::string key = tptz__RemovePreset->ProfileToken;
	std::vector<std::string> tokenList = _ptzKVC->keys();

	if (std::find(tokenList.begin(), tokenList.end(), key) == tokenList.end()) {
		soap_print_fault(stderr);
		set_SOAP_ENV__Fault(soap, "env:Sender", "ter:InvalidArgVal", "ter:NoEntity", "the requested profile token ProfileToken does not exist");

		return SOAP_ERR;
	}
	else {
		_ptzes[key]->preset_get(atoi(tptz__RemovePreset->PresetToken.c_str()));
	}

	return SOAP_OK;
}

int MyPtz::GetScales(_tptz__GetScales *tptz__GetScales, _tptz__GetScalesResponse *res)
{
	std::string key = tptz__GetScales->ProfileToken;
	std::vector<std::string> tokenList = _ptzKVC->keys();

	if (std::find(tokenList.begin(), tokenList.end(), key) == tokenList.end()) {
		soap_print_fault(stderr);
		set_SOAP_ENV__Fault(soap, "env:Sender", "ter:InvalidArgVal", "ter:NoEntity", "the requested profile token ProfileToken does not exist");

		return SOAP_ERR;
	}
	res->Scales = _ptzes[key]->getScales();

	return SOAP_OK;
}

int MyPtz::GetPtzParams(_tptz__GetPtzParams *tptz__GetPtzParams, _tptz__GetPtzParamsResponse *res)
{
	std::string key = tptz__GetPtzParams->ProfileToken;
	std::vector<std::string> tokenList = _ptzKVC->keys();

	if (std::find(tokenList.begin(), tokenList.end(), key) == tokenList.end()) {
		soap_print_fault(stderr);
		set_SOAP_ENV__Fault(soap, "env:Sender", "ter:InvalidArgVal", "ter:NoEntity", "the requested profile token ProfileToken does not exist");
		
		return SOAP_ERR;
	}
	PtzControlling::PtzParam params = _ptzes[key]->getPtzParam();
	res->PtzParams = soap_new_zonekey__ZonekeyPtzParamType(soap);

	res->PtzParams->ccd_USCOREsize_USCOREheight = params.ccd_size_height;
	res->PtzParams->ccd_USCOREsize_USCOREwidth = params.ccd_size_width;
	res->PtzParams->f = params.f;
	res->PtzParams->pan_USCOREmax_USCOREva = params.pan_max_va;
	res->PtzParams->pan_USCOREmin_USCOREangle = params.pan_min_angle;
	res->PtzParams->tilt_USCOREmax_USCOREva = params.tilt_max_va;
	res->PtzParams->tilt_USCOREmin_USCOREangle = params.tilt_min_angle;

	return SOAP_OK;
}

MyPtz::~MyPtz()
{
	std::map<std::string, PtzControlling *>::const_iterator c_it;
	for (c_it = _ptzes.begin(); c_it != _ptzes.end(); ++c_it) {
		c_it->second->close();
		delete(c_it->second);
	}
}

void MyPtz::run()
{
	if (soap_valid_socket(this->soap->master) || soap_valid_socket(bind(NULL, port_, 100)))
	{
		for (;;)
		{
			if (soap_valid_socket(accept()) && serve()) {
				soap_destroy(this->soap);
				soap_end(this->soap);
			}
			else {
				destroy();
			}
		}
	}
}

void set_SOAP_ENV__Fault(soap *soap, char *env, char *ter0, char *ter1, char *text)
{
	//FIXME:利用 memset, soap_type的值变为 0, 不知可否 ????
	soap->fault = soap_new_SOAP_ENV__Fault(soap);
	memset(soap->fault, 0, sizeof(SOAP_ENV__Fault));

	soap->fault->SOAP_ENV__Code = soap_new_SOAP_ENV__Code(soap);
	memset(soap->fault->SOAP_ENV__Code, 0, sizeof(SOAP_ENV__Fault));
	soap->fault->SOAP_ENV__Code->SOAP_ENV__Value = soap_strdup(soap, env);

	soap->fault->SOAP_ENV__Code->SOAP_ENV__Subcode = soap_new_SOAP_ENV__Code(soap);
	SOAP_ENV__Code *subcode = soap->fault->SOAP_ENV__Code->SOAP_ENV__Subcode;
	memset(subcode, 0, sizeof(SOAP_ENV__Code));
	subcode->SOAP_ENV__Value = soap_strdup(soap, ter0);
	subcode->SOAP_ENV__Subcode = soap_new_SOAP_ENV__Code(soap);
	memset(subcode->SOAP_ENV__Subcode, 0, sizeof(SOAP_ENV__Code));
	subcode->SOAP_ENV__Subcode->SOAP_ENV__Value = soap_strdup(soap, ter1);

	soap->fault->SOAP_ENV__Reason = soap_new_SOAP_ENV__Reason(soap);
	memset(soap->fault->SOAP_ENV__Reason, 0, sizeof(SOAP_ENV__Reason));
	soap->fault->SOAP_ENV__Reason->SOAP_ENV__Text = soap_strdup(soap, text);

}
//std::vector<tt__PTZConfiguration *> pConfigurations;

//tt__PTZConfiguration* new_soap_tt__PTZConfiguration(struct soap *soap, tt__PTZConfiguration *tpc);

//void delete_tt__PTZConfigurations(std::vector<tt__PTZConfiguration *> pConfigurations);

//
//	PTZ Configuration
//

//int MyPtz::GetConfigurations(_tptz__GetConfigurations *tptz__GetConfigurations, _tptz__GetConfigurationsResponse *tptz__GetConfigurationsResponse)
//{
//	struct soap *sp = tptz__GetConfigurationsResponse->soap;
//	std::vector<tt__PTZConfiguration *>::iterator c_it;
//	tptz__GetConfigurationsResponse->PTZConfiguration.clear();
//	for (c_it = pConfigurations.begin(); c_it != pConfigurations.end(); ++c_it) {
//		tt__PTZConfiguration *pc = new_soap_tt__PTZConfiguration(tptz__GetConfigurationsResponse->soap, *c_it);
//		tptz__GetConfigurationsResponse->PTZConfiguration.push_back(pc);
//	}
//	return SOAP_OK;
//	
//}
//
//int MyPtz::SetConfiguration(_tptz__SetConfiguration *tptz__SetConfiguration, 
//							_tptz__SetConfigurationResponse *tptz__SetConfigurationResponse)
//{
//	tt__PTZConfiguration *pPtzConfiguration = tptz__SetConfiguration->PTZConfiguration;
//	tt__PTZConfiguration *pConfiguration = new tt__PTZConfiguration(*pPtzConfiguration);
//	pConfiguration->NodeToken = pPtzConfiguration->NodeToken;
//
//	if (pPtzConfiguration->DefaultAbsolutePantTiltPositionSpace != NULL)
//		pConfiguration->DefaultAbsolutePantTiltPositionSpace = new std::string(*pPtzConfiguration->DefaultAbsolutePantTiltPositionSpace);
//
//	if (pPtzConfiguration->DefaultAbsoluteZoomPositionSpace != NULL)
//		pConfiguration->DefaultAbsoluteZoomPositionSpace = new std::string(*pPtzConfiguration->DefaultAbsoluteZoomPositionSpace);
//
//
//	if (pPtzConfiguration->DefaultContinuousPanTiltVelocitySpace != NULL)
//		pConfiguration->DefaultContinuousPanTiltVelocitySpace = new std::string(*pPtzConfiguration->DefaultContinuousPanTiltVelocitySpace);
//
//
//	if (pPtzConfiguration->DefaultContinuousZoomVelocitySpace != NULL)
//		pConfiguration->DefaultContinuousZoomVelocitySpace = new std::string(*pPtzConfiguration->DefaultContinuousZoomVelocitySpace);
//
//	if (pPtzConfiguration->DefaultPTZSpeed != NULL) {
//		pConfiguration->DefaultPTZSpeed = new tt__PTZSpeed(*pPtzConfiguration->DefaultPTZSpeed);
//		if (pPtzConfiguration->DefaultPTZSpeed->PanTilt != NULL)
//			pConfiguration->DefaultPTZSpeed->PanTilt = new tt__Vector2D(*pPtzConfiguration->DefaultPTZSpeed->PanTilt);
//		if (pPtzConfiguration->DefaultPTZSpeed->Zoom != NULL)
//			pConfiguration->DefaultPTZSpeed->Zoom = new tt__Vector1D(*pPtzConfiguration->DefaultPTZSpeed->Zoom);
//	}
//
//	if (pPtzConfiguration->DefaultPTZTimeout != NULL)
//		pConfiguration->DefaultPTZTimeout = new (LONG64)(*pPtzConfiguration->DefaultPTZTimeout);
//
//	if (pPtzConfiguration->DefaultRelativePanTiltTranslationSpace != NULL)
//		pConfiguration->DefaultRelativePanTiltTranslationSpace = new std::string(*pPtzConfiguration->DefaultRelativePanTiltTranslationSpace);
//
//	if (pPtzConfiguration->DefaultRelativeZoomTranslationSpace != NULL)
//		pConfiguration->DefaultRelativeZoomTranslationSpace = new std::string(*pPtzConfiguration->DefaultRelativeZoomTranslationSpace);
//
//	if (pPtzConfiguration->Extension != NULL) {
//		//	TODO:
//		;
//	}
//	
//	if (pPtzConfiguration->PanTiltLimits != NULL) {
//		//	TODO:
//		;
//	}
//
//	pConfigurations.push_back(pConfiguration);
//
//	return SOAP_OK;
//}
//
//int MyPtz::GetConfiguration(_tptz__GetConfiguration *tptz__GetConfiguration, _tptz__GetConfigurationResponse *tptz__GetConfigurationResponse)
//{	
//	std::vector<tt__PTZConfiguration *>::const_iterator c_it;
//	for (c_it = pConfigurations.begin(); c_it != pConfigurations.end(); ++c_it) {
//		if ((*c_it)->NodeToken == tptz__GetConfiguration->PTZConfigurationToken) {
//			tptz__GetConfigurationResponse->PTZConfiguration = new_soap_tt__PTZConfiguration(tptz__GetConfigurationResponse->soap, *c_it);
//			return SOAP_OK;
//		}
//	}
//
//	return SOAP_ERR;	//	FIXME: ...
//}

//tt__PTZConfiguration* new_soap_tt__PTZConfiguration(struct soap *soap, tt__PTZConfiguration *tpc)
//{
//	tt__PTZConfiguration *pc = soap_new_tt__PTZConfiguration(soap);
//	*pc = *tpc;
//
//	if (tpc->DefaultAbsolutePantTiltPositionSpace != NULL) {
//		pc->DefaultAbsolutePantTiltPositionSpace = soap_new_std__string(soap);
//		*pc->DefaultAbsolutePantTiltPositionSpace = *tpc->DefaultAbsolutePantTiltPositionSpace;
//	}
//	if (tpc->DefaultAbsoluteZoomPositionSpace != NULL) {
//		pc->DefaultAbsoluteZoomPositionSpace = soap_new_std__string(soap);
//		*pc->DefaultAbsoluteZoomPositionSpace = *tpc->DefaultAbsoluteZoomPositionSpace;
//	}
//	if (tpc->DefaultContinuousPanTiltVelocitySpace != NULL) {
//		pc->DefaultContinuousPanTiltVelocitySpace = soap_new_std__string(soap);
//		*pc->DefaultContinuousPanTiltVelocitySpace = *tpc->DefaultContinuousPanTiltVelocitySpace;
//	}
//	// TODO: continue ...
//
//	return pc;
//}
//
//void delete_tt__PTZConfigurations(std::vector<tt__PTZConfiguration *> pConfigurations)
//{
//	//TODO:当关机时,需要释放掉 configurations
//}
