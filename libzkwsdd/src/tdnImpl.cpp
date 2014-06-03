#include "soapH.h"

int __tdn__Hello(soap *soap, wsdd__HelloType hello, wsdd__ResolveType &res)
{
	return SOAP_OK;
}

int __tdn__Bye(soap *soap, wsdd__ByeType bye, wsdd__ResolveType &res)
{
	return SOAP_OK;
}

int __tdn__Probe(soap *soap, wsdd__ProbeType probe, wsdd__ProbeMatchesType &res)
{
	return SOAP_OK;
}
