/** 实现 event 接口 */

#pragma once
#include "../soap/soapPullPointSubscriptionBindingService.h"
#include "myservice.inf.h"
#include <cc++/thread.h>
#include <assert.h>
#include <algorithm>
#include "../../common/utils.h"
#include "../../common/log.h"
#include <vector>
#include <string>
#include <list>
#include <deque>
#include <sstream>

class MyEvent;

/** 一个订阅点，用于处理 PullMessage, Unsubscribe ...
	每个订阅点，都是一个独立的工作线程 ?
	
	FIXME: 仅仅收到 Unsubscribe 才结束，目前不做超时处理 ...
*/
class MyPullPoint : PullPointSubscriptionBindingService
				  , ost::Thread
				  , public ServiceInf
{
	MyEvent *evt_;
	std::string ns_, url_;
	bool quit_;
	int port_;
	unsigned timeout_without_connection_;	// 当持续此秒后，如果没有新的 pull message，则主动结束 ..
	time_t time_to_end_;	// 当前时间 + timeout

	struct NotifyMessage
	{
		std::string ns;	// ptz, media, ...
		std::string sid; // uuid ...
		int code;
		std::string info;
	};

	typedef std::deque<NotifyMessage> MESSAGES;
	MESSAGES pending_messages;
	ost::Mutex cs_pending_messages;
	ost::Semaphore sem_;

public:
	// FIXME: 根据 ns 构造通知点的匹配属性 ...
	MyPullPoint(MyEvent *evt, const char *ns, unsigned timeout = 30)
	{
		evt_ = evt;
		ns_ = ns;

		timeout_without_connection_ = timeout;
		time_to_end_ = time(0) + timeout;

		bind(0, 0, 100);
		
		sockaddr_in sin;
		socklen_t len = sizeof(sin);
		getsockname(soap->master, (sockaddr*)&sin, &len);
		port_ = ntohs(sin.sin_port);

		char buf[128];
		snprintf(buf, sizeof(buf), "http://%s:%d", util_get_myip(), port_);
		url_ = buf;

		quit_ = false;
		detach();
	}

	// 通知消息 ...
	int append(const char *ns, const char *sid, int code, const char *info);
	
	const char *url() const 
	{
		return url_.c_str();
	}

	const char *ns() const
	{
		return ns_.c_str();
	}

private:
	void run();

private:
	bool curr_msgs(std::vector<NotifyMessage> &msgs)
	{
		cs_pending_messages.enter();
		if (pending_messages.empty()) {
			cs_pending_messages.leave();
			return false;
		}
		else {
			for (MESSAGES::iterator it = pending_messages.begin(); it != pending_messages.end(); ++it) {
				msgs.push_back(*it);
			}
			pending_messages.clear();
			cs_pending_messages.leave();
			return true;
		}
	}

private:
	virtual int PullMessages(_tev__PullMessages *tev__PullMessages, _tev__PullMessagesResponse *tev__PullMessagesResponse);
	virtual int Unsubscribe(_wsnt__Unsubscribe *wsnt__Unsubscribe, _wsnt__UnsubscribeResponse *wsnt__UnsubscribeResponse);
	virtual int Renew(_wsnt__Renew *wsnt__Renew, _wsnt__RenewResponse *wsnt__RenewResponse);
};

/** 实现 udp 本地接收事件服务，启动后，接收 localhost 发出的 udp 消息 (PostEvent)，然后通过 ServiceEventSinkInf 接口发出通知 .

		典型的 servive 使用模式：


 */
class MyLocalEventRecver : PullPointSubscriptionBindingService
						 , ost::Thread
						 , public ServiceInf
{
	int port_;	// udp listen port
	ServiceEventSinkInf *sink_;

public:
	MyLocalEventRecver(int port, ServiceEventSinkInf *sink)
		: PullPointSubscriptionBindingService()
	{
		port_ = port;
		sink_ = sink;

		detach();	// 
	}

private:
	const char *url() const 
	{
		return "";
	}

	const char *ns() const
	{
		return "";
	}

	void run()
	{
		int rc = bind(0, port_, 100);
		if (!soap_valid_socket(rc)) {
			log(LOG_FAULT, "%s: Ohhhh, udp local bind error for port %d\n", __func__, port_);
			::exit(-1);
		}

		while (1) {
			if (soap_valid_socket(accept())) {
				serve();
				destroy();
			}
		}

		soap_done(soap);
	}

	virtual int LocalPostEvent(zonekey__ZonekeyPostMessageType *msg, char *&res)
	{
		assert(sink_);
		log(LOG_DEBUG, "%s: ns='%s', sid='%s', code='%d', info='%s'\n", __func__,
			msg->ns.c_str(), msg->sid.c_str(), msg->code, msg->info.c_str());
		sink_->post(msg->ns.c_str(), msg->sid.c_str(), msg->code, msg->info.c_str());
		res = soap_strdup(soap, "");

		return SOAP_OK;
	}
};

/** 实现 Real-time Pull-Point Notification Interface 模型  (core 9.2)  */
class MyEvent : PullPointSubscriptionBindingService
			  , ost::Thread
			  , public ServiceInf
			  , public ServiceEventSinkInf
{
	int port_;
	std::string url_;
	typedef std::list<MyPullPoint*> PULLPOINTS;
	PULLPOINTS pull_points_;
	ost::Mutex cs_pull_points_;
	MyLocalEventRecver *local_recver_;	// 用于 udp 本地监听 ..

	friend class MyPullPoint;

public:
	MyEvent(int port);
	virtual ~MyEvent();

private:
	const char *url() const { return url_.c_str(); }
	const char *ns() const
	{
		// FIXME: 这里应该照着规矩来 ...
		return "event";
	}

	/// 将消息发送到匹配的通知点 ...
	void post(const char *ns, const char *sid, int code, const char *info);

	void run();

	void remove_pullpoint(MyPullPoint *p)
	{
		ost::MutexLock al(cs_pull_points_);
		PULLPOINTS::iterator itf = std::find(pull_points_.begin(), pull_points_.end(), p);
		if (itf != pull_points_.end()) {
			pull_points_.erase(itf);
		}
	}

private:
	virtual	int GetServiceCapabilities(_tev__GetServiceCapabilities *tev__GetServiceCapabilities,
									   _tev__GetServiceCapabilitiesResponse *tev__GetServiceCapabilitiesResponse);

	virtual	int GetEventProperties(_tev__GetEventProperties *tev__GetEventProperties, 
								   _tev__GetEventPropertiesResponse *tev__GetEventPropertiesResponse);

	virtual	int CreatePullPointSubscription(_tev__CreatePullPointSubscription *tev__CreatePullPointSubscription,
											_tev__CreatePullPointSubscriptionResponse *tev__CreatePullPointSubscriptionResponse);
};

extern int evt_PostEvent(const char *ns, const char *sid, int code, const char *info);
