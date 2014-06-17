/**	Zonekey Source:
		实现 target 端的 device mgrt 接口
 */

#include "../../common/log.h"
#include "myservice.inf.h"
#include "MyEvent.h"
#include "MyPtz.h"
#include "MyDevice.h"
#include "MyDeviceDiscovery.h"

int main(int argc, char **argv)
{
	log_init();

	std::vector<ServiceInf *> services;

	MyPtz ptz(10001);	// 云台服务 ..
	services.push_back(&ptz);

	MyMediaStream ms;	// 直播服务 ..
	services.push_back(&ms);

	MyEvent evt(10000);	// 事件服务 ...
	services.push_back(&evt);

	MyDevice device(9999, services);
	MyDeviceDiscovery discovery(&device);

	while (1) {
		ost::Thread::sleep(100);
	}

	return 0;
}
