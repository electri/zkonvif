#pragma once
#include <cc++/config.h>
#include <string>
/** 这个用于方便 MyDevice 支持更多的服务 ...
注意： 这里的接口，需要根据 MyDevice 的 GetServices 实际需要进行扩展 .....
*/
class ServiceEventSinkInf;

class ServiceInf
{
public:
	virtual const char *url() const = 0;	// 所有的服务，都必须有个 url .
	virtual const char *desc() const { return ""; }	// 可选有个描述信息 ..
	virtual const char *ns() const = 0;	// 必须返回 namespace .
	virtual const char *sid() const = 0;//所有的服务必须返回sid，sid代表此类别下的唯一标识

	ServiceInf()
	{
		sink_ = 0;
	}

	void set_eventsink(ServiceEventSinkInf *sink)
	{
		sink_ = sink;
	}

protected:
	ServiceEventSinkInf *sink_;
};

/** 事件投递接口, 当有效时，服务的实现可以发布自己的异步事件 ..

		比如 ptz 服务：可以考虑投递一个转动到位的通知 :

			if (sink_)
				sink_->post(this->ns(), 2, 0, "set_pos ok ....");

		FIXME: 嗯，这里没有考虑 onvif 的 Topics, 直接简单点吧 :)
 */
class ServiceEventSinkInf
{
public:
	virtual void post(const char *ns, const char *sid, int code, const char *info) = 0;
};
