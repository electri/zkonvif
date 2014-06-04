/** 工作线程
 */

#pragma once

#include <deque>
#include <cc++/thread.h>
#include "Target_Client.h"

/** Target 工作线程，收到 probe/resolve 后，会依次查询 Target
 */
class TargetThread : ost::Thread
{
	bool quit_;

	typedef std::deque<Target*> FIFO;
	FIFO fifo_;
	ost::Mutex cs_fifo_;

public:
	TargetThread();
	~TargetThread();

	int bind(Target *target);
	int unbind(Target *target);

private:
	void run();
};
