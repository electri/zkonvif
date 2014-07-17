#include "../soap/soapPullPointSubscriptionBindingProxy.h"
#ifdef WITH_OPENSSL
#	include "../soap/wsseapi.h"
#endif // openssl
#include "../../common/log.h"
#include "../../common/utils.h"
#include "../../common/KVConfig.h"

// 测试设备管理 ...
void test_devicemgrt(const zonekey__ZonekeyDMServiceType *service)
{
	fprintf(stdout, "\n\n%s: url=%s\n", __FUNCTION__, service->url.c_str());
}
