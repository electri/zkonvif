#include "soapH.h"
#include "log.h"

int __wsdd__Hello(soap *soap, wsdd__HelloType *data)
{
	return SOAP_OK;
}

int __wsdd__Bye(soap *soap, wsdd__ByeType *data)
{
	return SOAP_OK;
}

int __wsdd__Probe(soap *soap, wsdd__ProbeType *data)
{
	log("%s: calling ...\n", __func__);
	return SOAP_OK;
}

int __wsdd__ProbeMatches(soap *soap, wsdd__ProbeMatchesType *data)
{
	return SOAP_OK;
}

int __wsdd__Resolve(soap *soap, wsdd__ResolveType *data)
{
	return SOAP_OK;
}

int __wsdd__ResolveMatches(soap *soap, wsdd__ResolveMatchesType *data)
{
	return SOAP_OK;
}
