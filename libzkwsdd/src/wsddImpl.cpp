#include "soapH.h"
#include "log.h"
#include "WorkingThread.h"
#include <assert.h>

int __wsdd__Hello(soap *soap, wsdd__HelloType *data)
{
	log("%s: calling ...\n", __func__);

	ThreadOpaque *opaque = (ThreadOpaque*)soap->user;
//	assert(!strcmp(opaque->name(), "client"));

	// TODO: client 处理收到的 Hello ...

	return SOAP_OK;
}

int __wsdd__Bye(soap *soap, wsdd__ByeType *data)
{
	log("%s: calling ...\n", __func__);

	ThreadOpaque *opaque = (ThreadOpaque*)soap->user;
	assert(!strcmp(opaque->name(), "client"));

	// TODO: client 处理收到的 Bye ... 

	return SOAP_OK;
}

static FILE *_fp = 0;

static int debug_before_send(soap *soap, const char *data, size_t len)
{
	if (_fp) {
		fprintf(_fp, "%s", data);
	}

	return 0;
}

static const char *my_messageid()
{
	static int _i = 0;
	static char buf[64];

	snprintf(buf, sizeof(buf), "id:%u", _i++);

	return buf;
}

int __wsdd__Probe(soap *soap, wsdd__ProbeType *data)
{
	log("%s: calling ...\n", __func__);
	log("\t: Types: %s, Scopes: %s\n", data->Types, data->Scopes ? data->Scopes->__item : "None");

	ThreadOpaque *opaque = (ThreadOpaque*)soap->user;
	assert(!strcmp(opaque->name(), "target"));

	TargetThread *th = (TargetThread*)opaque->th();

    //XXXX: 代码描述不清晰
	const char *type = 0, *scope = 0;
	
	std::vector<Target *> targets = th->probe_matched(type, scope);

	// 根据 targets 构造 ProbeMatches ...
	wsdd__ProbeMatchesType pms;
	pms.__sizeProbeMatch = targets.size();
	pms.ProbeMatch = (wsdd__ProbeMatchType *)soap_malloc(soap, pms.__sizeProbeMatch * sizeof(wsdd__ProbeMatchType));
	for (size_t i = 0; i < pms.__sizeProbeMatch; i++) {
		wsdd__ProbeMatchType *pm = &pms.ProbeMatch[i];

		pm->wsa__EndpointReference.Address = soap_strdup(soap, targets[i]->id());
		pm->wsa__EndpointReference.ReferenceParameters = 0;
		pm->wsa__EndpointReference.ReferenceProperties = 0;
		pm->wsa__EndpointReference.PortType = 0;
		pm->wsa__EndpointReference.ServiceName = 0;
		pm->wsa__EndpointReference.__size = 0;
		pm->wsa__EndpointReference.__any = 0;
		pm->wsa__EndpointReference.__anyAttribute = 0;

		pm->Types = soap_strdup(soap, "tdn:NetworkVideoTransmitter");

		pm->Scopes = (wsdd__ScopesType*)soap_malloc(soap, sizeof(wsdd__ScopesType));
		pm->Scopes->MatchBy = 0;
		pm->Scopes->__item = soap_strdup(soap, "onvif://www.onvif.org/type/NetworkVideoTransmitter");

		pm->XAddrs = soap_strdup(soap, targets[i]->url());

		pm->MetadataVersion = 1;
	}

	// 需要修改 wsa_Header
	SOAP_ENV__Header * header = soap->header;
	assert(header);

	// XXX: 必须的，否则 client 不知道这个 PM 是对应着那个 P
	header->wsa__RelatesTo = (wsa__Relationship *)soap_malloc(soap, sizeof(wsa__Relationship));
	header->wsa__RelatesTo->__item = soap_strdup(soap, header->wsa__MessageID);
	header->wsa__RelatesTo->__anyAttribute = 0;
	header->wsa__RelatesTo->RelationshipType = 0;

	header->wsa__MessageID = soap_strdup(soap, my_messageid());
	header->wsa__Action = 0;
	header->wsa__To = 0;

	// FIXME: 是否单播发送的??
	//		查看代码发现， soap->peer 保存了发送者的地址(非组播地址)
	soap->fpreparesend = debug_before_send;
	_fp = fopen("pm.xml", "w");
	soap_send___wsdd__ProbeMatches(soap, "http://", 0, &pms);
	fclose(_fp);
	soap->fpreparesend = 0;

	return SOAP_OK;
}

int __wsdd__ProbeMatches(soap *soap, wsdd__ProbeMatchesType *data)
{
	// TODO: 
	return SOAP_OK;
}

int __wsdd__Resolve(soap *soap, wsdd__ResolveType *data)
{
	// TODO: 
	log("%s: calling ...\n", __func__);
	log("\t:Address: %s...\n", data->wsa__EndpointReference.Address);

	ThreadOpaque *opaque = (ThreadOpaque*)soap->user;
	assert(!strcmp(opaque->name(), "target"));

	TargetThread *th = (TargetThread*)opaque->th();

	const char *type = 0, *scope = 0;

	std::vector<Target *> targets = th->resolve_matched(data->wsa__EndpointReference.Address);

	// 根据 targets 构造 ProbeMatches ...
	wsdd__ResolveMatchesType sms;
	sms.ResolveMatch = (wsdd__ResolveMatchType *)soap_malloc(soap, targets.size()*sizeof(wsdd__ResolveMatchType));

	for (size_t i = 0; i < targets.size(); i++) {
		wsdd__ResolveMatchType *sm = &sms.ResolveMatch[i];

		sm->wsa__EndpointReference.Address = soap_strdup(soap, targets[i]->id());
		sm->wsa__EndpointReference.ReferenceParameters = 0;
		sm->wsa__EndpointReference.ReferenceProperties = 0;
		sm->wsa__EndpointReference.PortType = 0;
		sm->wsa__EndpointReference.ServiceName = 0;
		sm->wsa__EndpointReference.__size = 0;
		sm->wsa__EndpointReference.__any = 0;
		sm->wsa__EndpointReference.__anyAttribute = 0;

		sm->Types = soap_strdup(soap, "tdn:NetworkVideoTransmitter");

		sm->Scopes = (wsdd__ScopesType*)soap_malloc(soap, sizeof(wsdd__ScopesType));
		sm->Scopes->MatchBy = 0;
		sm->Scopes->__item = soap_strdup(soap, "onvif://www.onvif.org/type/NetworkVideoTransmitter");

		sm->XAddrs = soap_strdup(soap, targets[i]->url());

		sm->MetadataVersion = 1;
	}

	// 需要修改 wsa_Header
	SOAP_ENV__Header * header = soap->header;
	assert(header);

	// XXX: 必须的，否则 client 不知道这个 PM 是对应着那个 P
	header->wsa__RelatesTo = (wsa__Relationship *)soap_malloc(soap, sizeof(wsa__Relationship));
	header->wsa__RelatesTo->__item = soap_strdup(soap, header->wsa__MessageID);
	header->wsa__RelatesTo->__anyAttribute = 0;
	header->wsa__RelatesTo->RelationshipType = 0;

	header->wsa__MessageID = soap_strdup(soap, my_messageid());
	header->wsa__Action = 0;
	header->wsa__To = 0;


	// FIXME: 是否单播发送的??
	//		查看代码发现， soap->peer 保存了发送者的地址(非组播地址)
	soap->fpreparesend = debug_before_send;
	_fp = fopen("sm.xml", "w");
	soap_send___wsdd__ResolveMatches(soap, "http://", 0, &sms);
	fclose(_fp);
	soap->fpreparesend = 0;

	return SOAP_OK;
}

int __wsdd__ResolveMatches(soap *soap, wsdd__ResolveMatchesType *data)
{
	// TODO:

	return SOAP_OK;
}
