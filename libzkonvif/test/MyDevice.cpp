#include "MyDevice.h"
#include <vector>
#include "../../common/log.h"

int MyDevice::GetServices(_tds__GetServices *tds__GetServices, _tds__GetServicesResponse *tds__GetServicesResponse)
{
	log(LOG_DEBUG, "%s: calling, en, there %u services...\n", __func__, services_.size());

	/** TODO: 这里应该返回 services_ 所有的服务信息 ...
	*/
	std::vector<ServiceInf*>::const_iterator it;
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

	return SOAP_OK;
}

int MyDevice::GetDeviceInformation(_tds__GetDeviceInformation *tds__GetDeviceInformation, _tds__GetDeviceInformationResponse* tds__GetDeviceInformationResponse)
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

int MyDevice::CreateUsers(_tds__CreateUsers *tds__CreateUsers, _tds__CreateUsersResponse *tds__CreateUsersResponse)
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