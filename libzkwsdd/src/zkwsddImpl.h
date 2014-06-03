#pragma once

#include "../include/zkwsdd.h"
#include <cc++/thread.h>

class zkwsdd_TargetImpl : ost::Thread
{
	bool quit_;
public:
	zkwsdd_TargetImpl(const char *id, const char *type, const char *url);
	~zkwsdd_TargetImpl();

private:
	void run();
};

class zkwsdd_ClientImpl
{
public:
};
