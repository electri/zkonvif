#pragma once

#include "../soap/soapDeviceBindingService.h"
#include <cc++/thread.h>
#include "../../common/utils.h"
#include "myservice.inf.h"
#include "../../common/log.h"
#include <map>
#include <sstream>

/** 实现一个接口,本质就是重载 gsoap 生成的 xxxService类, 然后具体实现所有"纯虚函数"


  	WARNING: GetAllServices() 返回所有配置的服务，这个配置于动态注册需要匹配起来 ...
 */
class MyDevice : DeviceBindingService
			   , ost::Thread
{
	int listen_port_;
	std::string url_;
	std::string id_;
	typedef std::vector<ServiceInf *> SERVICES;
	SERVICES services_; // 这个设备上, 聚合的所有服务的列表 ...
	std::vector<tt__User *> users_; //这个设备上，聚合的所有user的列表...

	// 模拟本地服务 ..
	class LocalService : public ServiceInf
	{
		std::string ns_, url_, desc_, sid_, service_name_;
		double stamp_;	// 用于检测是否超时 ...
		int id_;

	public:
		LocalService(const char *ns, const char *url, 
				const char *desc, const char *sid, const char *service_name, int id)
		{
			ns_ = ns, desc_ = desc, url_ = url;
			sid_ = sid, service_name_ = service_name;
			id_ = id;
			stamp_ = util_now();
		}

		const char *ns() const { return ns_.c_str(); }
		const char *desc() const { return desc_.c_str(); }
		const char *url() const { return url_.c_str(); }
		const char *sid() const { return sid_.c_str(); }
		const char *name() const { return service_name_.c_str(); }
		const int id() const { return id_; }

		bool is_service() const 
		{
			// FIXME: 通过判断 service_name_ 中是否包含目录分隔符号来判断 ..
#ifdef WIN32
			return strchr(name(), '\\') != 0;
#else
			return strchr(name(), '/') != 0;
#endif // 
		}

#define HB_TIMEOUT 25.0
		bool is_timeout(double curr) const
		{
			return curr - stamp_ > HB_TIMEOUT;
		}

		void update_hb()
		{
			stamp_ = util_now();
		}
	};


	typedef std::map<int, LocalService*> LSERVICES;	
	LSERVICES local_services_;
	ost::Mutex cs_local_services_;

public:
	MyDevice(int listen_port, const std::vector<ServiceInf *> &services)
	{
		std::vector<ServiceInf*>::const_iterator it;
		for (it = services.begin(); it != services.end(); ++it)
			services_.push_back(*it);

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

	std::string next_sid(const char *ns)
	{
		static unsigned int _nid = 1;
		std::stringstream ss;
		ss << util_get_mymac() << '_' << ns << '_' << _nid++;
		return ss.str();
	}

	int next_id()
	{
		static int _id = 1;
		return _id++;
	}

	void check_hb_timeouted();

private:
	/// 下面实现 device mgrt 接口...
	virtual int GetServices(_tds__GetServices *tds__GetServices, _tds__GetServicesResponse *tds__GetServicesResponse);

	// 测试工具会调用这里,填充信息 ...
	virtual int GetDeviceInformation(_tds__GetDeviceInformation *tds__GetDeviceInformation, 
			_tds__GetDeviceInformationResponse *tds__GetDeviceInformationResponse);

	// This operation lists the registered users and along with their user levels
	virtual	int GetUsers(_tds__GetUsers *tds__GetUsers, _tds__GetUsersResponse *tds__GetUsersResponse);

	// This operation creates new device users and corresponding credentials on a device for authentication
	virtual	int CreateUsers(_tds__CreateUsers *tds__CreateUsers, _tds__CreateUsersResponse *tds__CreateUsersResponse);

	// This operation deletes users on a device
	virtual	int DeleteUsers(_tds__DeleteUsers *tds__DeleteUsers, _tds__DeleteUsersResponse *tds__DeleteUsersResponse);

	// This operation updates the settings for one or several users on a device for authentication
	virtual	int SetUser(_tds__SetUser *tds__SetUser, _tds__SetUserResponse *tds__SetUserResponse);

	/** 维护本地服务列表 ... 
	 */
	virtual int RegService(_tds__ServMgrtRegService *req, _tds__ServMgrtRegServiceResponse *res);
	virtual int UnregService(_tds__ServMgrtUnregService *req, _tds__ServMgrtUnregServiceResponse *res);
	virtual int Heartbeat(_tds__ServMgrtHeartbeat *req, _tds__ServMgrtHeartbeatResponse *res);
};

