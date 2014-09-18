#include <stdio.h>
#include <stdlib.h>
#include "../include/zkwsdd.h"
#include <cc++/thread.h>

// 模拟 Target
class MyTarget : public zkwsdd_Target
{
public:
	MyTarget() : zkwsdd_Target("urn:uuid:1111-0000", "eval", "rtmp://172.16.1.10:4433")
	{
	}
};

int main(int argc, char **argv)
{
	MyTarget target;

	while (1) {
        ost::Thread::sleep(100);
	}

	return 0;
}
