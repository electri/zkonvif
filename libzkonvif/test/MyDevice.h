#pragma once

#include "../soap/soapDeviceBindingService.h"
#include <cc++/thread.h>
#include "../../common/utils.h"
#include "myservice.inf.h"
#include "../../common/log.h"

/** 实现一个接口,本质就是重载 gsoap 生成的 xxxService类, 然后具体实现所有"纯虚函数"
 */
class MyDevice : DeviceBindingService
				, ost::Thread
{
	int listen_port_;
	std::string url_;
	std::string id_;
	std::vector<ServiceInf *> services_; // 这个设备上, 聚合的所有服务的列表 ...
	std::vector<tt__User *> users_; //这个设备上，聚合的所有user的列表...

public:
	MyDevice(int listen_port, const std::vector<ServiceInf *> &services)
	{
		services_ = services;

		listen_port_ = listen_port;
		char buf[128];

		snprintf(buf, sizeof(buf), "http://%s:%d", util_get_myip(), listen_port_);
		url_ = buf;

		log(LOG_INFO, "%s: device mgrt using url='%s'\n", __func__, url_.c_str());

		/** 使用 mac 地址作为 id */
		snprintf(buf, sizeof(buf), "urn:uuid:%s", util_get_mymac());
		id_ = buf;

		start();	// 启动工作线程
	}

	const char *id() const { return id_.c_str(); }
	const char *url() const { return url_.c_str(); }

private:
	void run()
	{
		DeviceBindingService::run(listen_port_);
	}
private:
	/// 下面实现 device mgrt 接口...
	virtual int GetServices(_tds__GetServices *tds__GetServices, _tds__GetServicesResponse *tds__GetServicesResponse);

	// 测试工具会调用这里,填充信息 ...
	virtual int GetDeviceInformation(_tds__GetDeviceInformation *tds__GetDeviceInformation, _tds__GetDeviceInformationResponse *tds__GetDeviceInformationResponse);

	// This operation lists the registered users and along with their user levels
	virtual	int GetUsers(_tds__GetUsers *tds__GetUsers, _tds__GetUsersResponse *tds__GetUsersResponse);

	// This operation creates new device users and corresponding credentials on a device for authentication
	virtual	int CreateUsers(_tds__CreateUsers *tds__CreateUsers, _tds__CreateUsersResponse *tds__CreateUsersResponse);

	// This operation deletes users on a device
	virtual	int DeleteUsers(_tds__DeleteUsers *tds__DeleteUsers, _tds__DeleteUsersResponse *tds__DeleteUsersResponse);

	// This operation updates the settings for one or several users on a device for authentication
	virtual	int SetUser(_tds__SetUser *tds__SetUser, _tds__SetUserResponse *tds__SetUserResponse);


};
