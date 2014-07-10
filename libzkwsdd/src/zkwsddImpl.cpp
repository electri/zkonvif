#include "zkwsddImpl.h"
#include "WorkingThread.h"
#include <assert.h>

static TargetThread *_targetThread = 0;

zkwsdd_Target::zkwsdd_Target(const char *id, const char *type, const char *url)
{
	internal_impl = new zkwsdd_TargetImpl(id, type, url);
}

zkwsdd_Target::~zkwsdd_Target()
{
	delete (zkwsdd_TargetImpl*)internal_impl;
}

zkwsdd_TargetImpl::zkwsdd_TargetImpl(const char *id, const char *type, const char *url)
{
	assert(id && type);
	id_ = id, type_ = type;

	if (!url) 
		url_ = "";
	else
		url_ = url;

	if (!_targetThread)
		_targetThread = new TargetThread;

	_targetThread->bind(this);
}

zkwsdd_TargetImpl::~zkwsdd_TargetImpl()
{
	assert(_targetThread);
	_targetThread->unbind(this);
}
