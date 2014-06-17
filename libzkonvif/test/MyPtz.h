#include "../soap/soapPTZBindingService.h"
#include <cc++/thread.h>
#include "myservice.inf.h"
#include "../../common/utils.h"

/** ÔÆÌ¨½Ó¿Ú
 */
class MyPtz : PTZBindingService
	, ost::Thread
	, public ServiceInf
{
	std::string url_;
	int port_;

public:
	MyPtz(int listen_port)
	{
		port_ = listen_port;

		char buf[128];
		snprintf(buf, sizeof(buf), "http://%s:%d", util_get_myip(), listen_port);

		url_ = buf;

		start();
	}

private:
	void run()
	{
		PTZBindingService::run(port_);
	}

	const char *url() const { return url_.c_str(); }
};