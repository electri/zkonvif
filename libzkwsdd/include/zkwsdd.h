/** zonekey onvif

		zkwsdd_Target: 方便实现 onvif target

		class MyService : public wsdd_Target
		{
		public:
			MyService(id, "ptz", "http://xxxx");
		};


		MyService *ptz_service = new MyService("xxxx");
		...
 */

#pragma once

#ifdef WIN32
#	ifdef LIBZKWSDD_EXPORTS
#		define ZKWSDD_API __declspec(dllexport)
#	else
#		define ZKWSDD_API __declspec(dllimport)
#	endif
#else
#	define ZKWSDD_API
#endif 

/** Target 基类，构造时发送 Hello，析构时发送 Bye
 */
class ZKWSDD_API zkwsdd_Target
{
public:
	zkwsdd_Target(const char *id,	// 对应 EndpointReference.Address，一般格式为 urn:xxxx-xxxx....
		const char *type = "eval",	// 对应 Type，目前仅仅支持 eval 和 ptz 两种
		const char *url = 0);		// 对应 XAddrs

	virtual ~zkwsdd_Target();

private:
	void *internal_impl;	// 内部实现，绝对不要动 :)
};
