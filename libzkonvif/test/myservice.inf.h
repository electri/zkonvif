#pragma once
#include <cc++/config.h>
#include <string>
/** 这个用于方便 MyDevice 支持更多的服务 ...
注意： 这里的接口，需要根据 MyDevice 的 GetServices 实际需要进行扩展 .....
*/
class ServiceInf
{
public:
	virtual const char *url() const = 0;	// 所有的服务，都必须有个 url .
	virtual const char *desc() const { return ""; }	// 可选有个描述信息 ..
	virtual const char *ns() const = 0;	// 必须返回 namespace .
};

/** rtmp 服务接口, 这个仅仅为了演示如何使用 ServiceInf
 */
class MyMediaStream : public ServiceInf
{
	std::string url_;

public:
	MyMediaStream()
	{
		url_ = "rtmp://0.0.0.0:0"; // FIXME: 一个非法的 url :)
	}

private:
	const char *url() const { return url_.c_str(); }
	const char *desc() const { return "zonekey RTMP living cast ...!"; }
	const char *ns() const 
	{
		// FIXME: 这里应该照着规矩来 ...
		return "media";
	}

private:
	static const char* my_messageid()
	{
		static int _i = 0;
		static char buf[64];

		snprintf(buf, sizeof(buf), "id:%u", _i++);

		return buf;
	}
};