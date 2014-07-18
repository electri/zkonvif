#include "MyDevice.h"
#include <vector>
#include "../../common/log.h"
#include <algorithm>

int MyDevice::GetServices(_tds__GetServices *tds__GetServices,
		_tds__GetServicesResponse *tds__GetServicesResponse)
{
	log(LOG_DEBUG, "%s: calling, en, there %u services...\n", __func__, services_.size());

	/** TODO: 这里应该返回 services_ 所有的服务信息 ...
	*/
	SERVICES::const_iterator it;
	for (it = services_.begin(); it != services_.end(); ++it) {
		/// TODO: ...
		///	url = it->url() ..
		/// desc = it->desc() ..
		/// namespace = it->ns() ..
		zonekey__ZonekeyDMServiceType *s = soap_new_zonekey__ZonekeyDMServiceType(soap);
		s->ns = (*it)->ns();
		s->url = (*it)->url();
		s->sid = (*it)->sid();
		s->desc = (*it)->desc();

		tds__GetServicesResponse->Service.push_back(s);
	}

	check_hb_timeouted();

	ost::MutexLock al(cs_local_services_);
	LSERVICES::const_iterator itl;
	for (itl = local_services_.begin(); itl != local_services_.end(); ++itl) {
		zonekey__ZonekeyDMServiceType *s = soap_new_zonekey__ZonekeyDMServiceType(soap);
		s->ns = (*itl).second->ns();
		s->url = (*itl).second->url();
		s->sid = (*itl).second->sid();
		s->desc = (*itl).second->desc();

		tds__GetServicesResponse->Service.push_back(s);
	}

	return SOAP_OK;
}

int MyDevice::GetDeviceInformation(_tds__GetDeviceInformation *tds__GetDeviceInformation, 
		_tds__GetDeviceInformationResponse* tds__GetDeviceInformationResponse)
{
	tds__GetDeviceInformationResponse->Manufacturer = "zonekey";
	tds__GetDeviceInformationResponse->Model = "ptz";
	tds__GetDeviceInformationResponse->FirmwareVersion = "0.0.1";
	tds__GetDeviceInformationResponse->HardwareId = util_get_mymac();
	tds__GetDeviceInformationResponse->SerialNumber = "11001";

	return SOAP_OK;
}

int MyDevice::GetUsers(_tds__GetUsers *tds__GetUsers, _tds__GetUsersResponse *tds__GetUsersResponse)
{
	log(LOG_DEBUG, "%s: calling, en, there %u users...\n", __func__, users_.size());

	//password is not included into the response
	std::vector<tt__User*>::const_iterator it;
	for (it = users_.begin(); it != users_.end(); ++it) {
		tt__User *u = soap_new_tt__User(soap);
		u->Username = (*it)->Username;
		u->UserLevel = (*it)->UserLevel;
		tds__GetUsersResponse->User.push_back(u);
	}	

	return SOAP_OK;
}

int MyDevice::CreateUsers(_tds__CreateUsers *tds__CreateUsers, 
		_tds__CreateUsersResponse *tds__CreateUsersResponse)
{
	std::vector<tt__User*>::const_iterator it;
	SOAP_ENV__Fault * fault = tds__CreateUsersResponse->soap->fault;
	for (it = tds__CreateUsers->User.begin(); it != tds__CreateUsers->User.end(); ++it) {
		std::vector<tt__User*>::const_iterator it_1;
		for (it_1 = users_.begin(); it_1 != users_.end(); ++it_1){
			if ((*it)->Username == (*it_1)->Username){
				fault->SOAP_ENV__Code->SOAP_ENV__Value = soap_strdup(soap, "env:Sender");
				fault->SOAP_ENV__Code->SOAP_ENV__Subcode->SOAP_ENV__Value = soap_strdup(soap, "ter:OperationProhibited");
				fault->SOAP_ENV__Code->SOAP_ENV__Subcode->SOAP_ENV__Subcode->SOAP_ENV__Value = soap_strdup(soap, "ter:UsernameClash");
				fault->SOAP_ENV__Reason->SOAP_ENV__Text = soap_strdup(soap, "Username already exists");
				return SOAP_USER_ERROR;
			}
		}
		if ((*(*it)->Password).size()>30){
			fault->SOAP_ENV__Code->SOAP_ENV__Value = soap_strdup(soap, "env:Sender");
			fault->SOAP_ENV__Code->SOAP_ENV__Subcode->SOAP_ENV__Value = soap_strdup(soap, "ter:OperationProhibited");
			fault->SOAP_ENV__Code->SOAP_ENV__Subcode->SOAP_ENV__Subcode->SOAP_ENV__Value = soap_strdup(soap, "ter:PasswordTooLong");
			fault->SOAP_ENV__Reason->SOAP_ENV__Text = soap_strdup(soap, "The password is too long");
			return SOAP_USER_ERROR;
		}
		users_.push_back(*it);
	}

	return SOAP_OK;
}

int MyDevice::DeleteUsers(_tds__DeleteUsers *tds__DeleteUsers, _tds__DeleteUsersResponse *tds__DeleteUsersResponse)
{
	return SOAP_OK;
}

int MyDevice::SetUser(_tds__SetUser *tds__SetUser, _tds__SetUserResponse *tds__SetUserResponse)
{
	return SOAP_OK;
}

int MyDevice::RegService(_tds__ServMgrtRegService *req, _tds__ServMgrtRegServiceResponse *res)
{
	std::string sid = next_sid(req->Register->ns.c_str());
	int id = next_id();

	LocalService *service = new LocalService(req->Register->ns.c_str(),
			req->Register->url.c_str(), req->Register->desc.c_str(),
			sid.c_str(), req->Register->addr.c_str(), id);

	res->Register = soap_new_zonekey__ZonekeyDMServRegisterResponseType(soap);
	res->Register->id = id;
	res->Register->sid = sid;

	ost::MutexLock al(cs_local_services_);
	local_services_[id] = service;

	log(LOG_DEBUG, "DEBUG: %s: local service reg: ns=%s, sid=%s, url=%s, id=%d\n",
			__func__, service->ns(), service->sid(), service->url(), service->id());

	return SOAP_OK;
}

int MyDevice::UnregService(_tds__ServMgrtUnregService *req, _tds__ServMgrtUnregServiceResponse *res)
{
	ost::MutexLock al(cs_local_services_);
	LSERVICES::iterator itf = local_services_.find(req->Unregister->id);
	if (itf != local_services_.end()) {
		log(LOG_DEBUG, "DEBUG: %s: local service unreg: ns=%s, sid=%s, url=%s, id=%d\n",
				__func__, itf->second->ns(), itf->second->sid(), itf->second->url(), itf->second->id());

		delete itf->second;
		local_services_.erase(itf);
	}
	else {
		// FIXME: 没有找到，是否返回错误 ??
		//		  目前看起来，不理他没关系 ..
	}
	return SOAP_OK;
}

int MyDevice::Heartbeat(_tds__ServMgrtHeartbeat *req, _tds__ServMgrtHeartbeatResponse *res)
{
	ost::MutexLock al(cs_local_services_);
	LSERVICES::iterator itf = local_services_.find(req->Heartbeat->id);
	if (itf != local_services_.end()) {
		itf->second->update_hb();

		log(LOG_DEBUG, "DEBUG: %s: local service hb: ns=%s, sid=%s, url=%s, id=%d\n",
				__func__, itf->second->ns(), itf->second->sid(), itf->second->url(), itf->second->id());
	}
	else {
		// FIXME: 没有找到，是否返回错误 ??
	}
	return SOAP_OK;
}

void MyDevice::check_hb_timeouted()
{
	/** 检查是否 local_services_ 是否心跳超时 */
	ost::MutexLock al(cs_local_services_);
	LSERVICES::iterator it, it2;
	double now = util_now();
	for (it = local_services_.begin(); it != local_services_.end(); ) {
		it2 = it, ++it2;
		if (it->second->is_timeout(now)) {
			fprintf(stderr, "WARNING: %s: service:ns=%s, sid=%s timeouted!!!\n",
					__func__, it->second->ns(), it->second->sid());
			delete it->second;
			local_services_.erase(it);
		}

		it = it2;
	}
}

