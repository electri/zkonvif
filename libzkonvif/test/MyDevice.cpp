#include "MyDevice.h"
#include <vector>

int MyDevice::GetServices(_tds__GetServices *tds__GetServices, _tds__GetServicesResponse *tds__GetServicesResponse)
{
	/** TODO: 这里应该返回 services_ 所有的服务信息 ...
	*/
	std::vector<ServiceInf*>::const_iterator it;
	for (it = services_.begin(); it != services_.end(); ++it) {
		/// TODO: ...
		///	url = it->url() ..
		/// desc = it->desc() ..
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