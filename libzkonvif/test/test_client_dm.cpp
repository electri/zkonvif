/** 测试程序： 测试 test_target_dm: 
		1. 输入 devicemgrt url:
		2. 从 devicemgrt 接口，查询得到其他服务接口 (url) .
		3. 对 url 进行测试 ...
 */

#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <cc++/thread.h>
#include "../soap/soapDeviceBindingProxy.h"
#include "../soap/soapPullPointSubscriptionBindingProxy.h"
#include "../soap/soapPTZBindingProxy.h"

typedef void(*pfn_test_service)(const tds__Service *service);

struct TestServiceFunc
{
	const char *ns;  // 对应 tds__Service 的 namespace, 用于区分测试类别 ...
	pfn_test_service func;
};

static void test_ptz(const tds__Service *);
static void test_event(const tds__Service *);

static TestServiceFunc _test_service_func_table[] = {
		{ "http://....", test_ptz, },
		{ "https://...", test_event, },
		{ 0, 0 },
};

static pfn_test_service get_test_ptr(const char *ns)
{
	assert(ns);

	TestServiceFunc *p = _test_service_func_table;
	while (p->ns) {
		if (!strcmp(p->ns, ns))
			return p->func;

		p++;
	}

	return 0;
}

int main(int argc, char **argv)
{
	if (argc != 2) {
		fprintf(stderr, "usage: %s <device mgrt url>\n", argv[0]);
		return -1;
	}

	const char *url = argv[1];

	fprintf(stdout, "using device mgrt url: '%s'\n", url);

	// device mgrt ...
	DeviceBindingProxy dbp(url);

	_tds__GetServices req_gs;
	_tds__GetServicesResponse res_gs;

	req_gs.IncludeCapability = false;

	int rc = dbp.GetServices(&req_gs, &res_gs);
	if (rc != SOAP_OK) {
		fprintf(stderr, "%s: dbp.GetServices err, code=%d\n", __FUNCTION__, rc);
		return -2;
	}

	// 测试每个服务 .
	std::vector<tds__Service *>::const_iterator it;
	for (it = res_gs.Service.begin(); it != res_gs.Service.end(); ++it) {
		const char *ns = (*it)->Namespace.c_str();
		pfn_test_service func = get_test_ptr(ns);
		if (func) func(*it);
	}

	fprintf(stdout, "test ... end ...\n");

	return 0;
}

// 测试云台 ...
static void test_ptz(const tds__Service *service)
{
}

// 测试事件 ...
static void test_event(const tds__Service *service)
{
}
