/** 此demo展示了一个服务，如何将自身注册到本级 dm */

#include <stdio.h>
#include <stdlib.h>
#include "../libzkreg/lcreg.h"
#include "../../common/utils.h"
#include <cc++/thread.h>
#include <cc++/HTTPServer.h>

class MyReqHandler : public zonekey::RequestHandler
{
public:

};

class MyFactory : public zonekey::RequestHandlerFactory
{
	zonekey::RequestHandler *create()
	{
		return new MyReqHandler();
	}
};

int main()
{
	MyFactory fac;
	zonekey::HTTPServer server(20000, &fac);

	ost::Thread::sleep(100000000);

	char url[128];
	snprintf(url, sizeof(url), "test://%s:0", util_get_myip());

	fprintf(stderr, "en, using url: '%s'\n", url);

	lc_regdesc_t desc;
	desc.ns = "test";
	desc.url = url;
	desc.desc = "a test service";
	desc.service_name = 0;

	lc_reg(&desc);

	// Now, todo anything ...
	while (1) {
		ost::Thread::sleep(1000);
	}

	lc_unreg();

	return 0;
}

