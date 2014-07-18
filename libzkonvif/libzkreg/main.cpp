#include <stdio.h>
#include <stdlib.h>
#include "lcreg.h"
#include "../soap/soapDeviceBindingProxy.h"
#include <cc++/thread.h>
#include <string>
#include <assert.h>
#ifdef linux
#	include <unistd.h>
#endif

namespace {
	// 启动工作线程，调用 dm 的 regService，并周期 HeartBeat ...
	struct Ctx : ost::Thread
	{
		std::string ns_, url_, name_, desc_;
		bool quit_;
		ost::Event exit_;

	public:
		Ctx(const lc_regdesc_t *desc)
		{
			assert(desc->ns && desc->url);
			ns_ = desc->ns, url_ = desc->url;

			if (desc->desc) desc_ = desc->desc; else desc_ = "";
			if (desc->service_name) 
				name_ = desc->service_name; 
			else {
#ifdef linux
				char name[1024] = {0};
				readlink("/proc/self/exe", name, sizeof(name));
				name_ = name;
#else
				char name[1024] = {0};
				GetModuleFileName(0, name, sizeof(name));
				name_ = name;
#endif
			}

			quit_ = false;
			start();
		}

		~Ctx()
		{
			quit_ = true;
			exit_.signal();
			join();
		}

	private:
		void run()
		{
			bool reged = false;
			int id;
			std::string sid;

			while (!quit_) {
				if (!reged)
					reged = reg(id, sid);

				if (exit_.wait(10000)) continue;

				if (reged)
					hb(id);
			}

			if (reged)
				unreg(id);
		}

		// TODO: 返回本级 dm 
		const char *endp() const
		{
			return "http://localhost:10000";
		}

		bool reg(int &id, std::string &sid)
		{
			// 注册 ..
			DeviceBindingProxy dbp;
			_tds__ServMgrtRegService req;
			req.Register = soap_new_zonekey__ZonekeyDMServRegisterType(dbp.soap);
			req.Register->url = url_;
			req.Register->desc = desc_;
			req.Register->ns = ns_;
			req.Register->addr = name_;

			_tds__ServMgrtRegServiceResponse res;
			
			if (dbp.RegService(endp(), 0, &req, &res) == SOAP_OK) {
				id = res.Register->id;
				sid = res.Register->sid;
				return true;
			}
			else
				return false;
		}

		void unreg(int id)
		{
			// 注销 ..
			DeviceBindingProxy dbp;
			_tds__ServMgrtUnregService req;
			req.Unregister = soap_new_zonekey__ZonekeyDMServUnregisterType(dbp.soap);
			req.Unregister->id = id;

			_tds__ServMgrtUnregServiceResponse res;

			dbp.UnregService(endp(), 0, &req, &res);
		}

		void hb(int id)
		{
			// 心跳 ..
			DeviceBindingProxy dbp;
			_tds__ServMgrtHeartbeat req;
			req.Heartbeat = soap_new_zonekey__ZonekeyDMServHeartbeatType(dbp.soap);
			req.Heartbeat->id = id;

			_tds__ServMgrtHeartbeatResponse res;

			dbp.Heartbeat(endp(), 0, &req, &res);
		}
	};
};

static Ctx *_ctx = 0;

void lc_reg(const lc_regdesc_t *desc)
{
	if (!_ctx)
		_ctx = new Ctx(desc);
}

void lc_unreg()
{
	delete _ctx;
	_ctx = 0;
}

