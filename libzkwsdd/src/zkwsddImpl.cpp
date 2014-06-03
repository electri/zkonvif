#include "zkwsddImpl.h"

zkwsdd_Target::zkwsdd_Target(const char *id, const char *type, const char *url)
{
	internal_impl = new zkwsdd_TargetImpl(id, type, url);
}

zkwsdd_Target::~zkwsdd_Target()
{
	delete (zkwsdd_TargetImpl*)internal_impl;
}

zkwsdd_Client::zkwsdd_Client()
{

}

zkwsdd_Client::~zkwsdd_Client()
{

}

void zkwsdd_Client::updated()
{

}

int zkwsdd_Client::probe()
{
	return -1;
}

int zkwsdd_Client::resolve()
{
	return -1;
}

zkwsdd_TargetImpl::zkwsdd_TargetImpl(const char *id, const char *type, const char *url)
{
	quit_ = false;
	start();
}

zkwsdd_TargetImpl::~zkwsdd_TargetImpl()
{
	quit_ = true;
	join();
}

void zkwsdd_TargetImpl::run()
{
	// TODO: 工作线程 ...
}
