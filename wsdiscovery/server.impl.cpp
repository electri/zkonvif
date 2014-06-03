#include "soapH.h"

#define SMALL_INFO_LENGTH 20
#define IP_LENGTH 20
#define INFO_LENGTH 100

static int GetIpList( char* vecIpList, int &nIpCount )
{
	char host_name[255]={0};
	if (gethostname(host_name, sizeof(host_name)) == -1) {
		return 1;
	}
	//printf("Host name is: %s\n", host_name);
	struct hostent *phe = gethostbyname(host_name);
	if (phe == 0) {
		return 1;
	}

	for (int i = 0; phe->h_addr_list[i] != 0; ++i) {
		struct in_addr addr;
		memcpy(&addr, phe->h_addr_list[i], sizeof(struct in_addr));
		//printf("Address %d : %s\n" , i, inet_ntoa(addr));
		strcpy(vecIpList+i*20 , inet_ntoa(addr) );
		nIpCount ++;
	}

	return 0;
}



SOAP_FMAC5 int SOAP_FMAC6 __wsdd__Hello(struct soap*, struct wsdd__HelloType *wsdd__Hello)
{
	return -1;
}

SOAP_FMAC5 int SOAP_FMAC6 __wsdd__Bye(struct soap*, struct wsdd__ByeType *wsdd__Bye)
{
	return -1;
}


SOAP_FMAC5 int SOAP_FMAC6 __wsdd__Probe(struct soap* soap, struct wsdd__ProbeType *wsdd__Probe)
{
	fprintf(stderr, "%s: calling ...\n", __func__);

	char _HwId[64]="urn:uuid:D149F919-4013-437E-B480-3707D96D27A4";

	int  interface_num = 0;
	char ip_list[512]={0};
	// Auto - get local ip address , return back this ip-address
	GetIpList( ip_list , interface_num);

	wsdd__ProbeMatchesType ProbeMatches;
	ProbeMatches.__sizeProbeMatch = interface_num;
	ProbeMatches.ProbeMatch = (struct wsdd__ProbeMatchType *)soap_malloc(soap, 
			sizeof(struct wsdd__ProbeMatchType)*interface_num);

	for(int i=0; i<interface_num; i++) {
		ProbeMatches.ProbeMatch[i].MetadataVersion = 1;
		// should be onvif device mgmt address
		ProbeMatches.ProbeMatch[i].XAddrs = (char *)soap_malloc(soap, sizeof(char) * INFO_LENGTH);
		sprintf(ProbeMatches.ProbeMatch[i].XAddrs, "http://%s:45678/", ip_list+i*20);
		// probe type
		ProbeMatches.ProbeMatch[i].Types = (char *)soap_malloc(soap, sizeof(char) * INFO_LENGTH);
		strcpy( ProbeMatches.ProbeMatch[i].Types , "tdn:NetworkVideoTransmitter" );
		// Scope
		ProbeMatches.ProbeMatch[i].Scopes = (struct wsdd__ScopesType*)soap_malloc(soap,sizeof(struct wsdd__ScopesType));
		ProbeMatches.ProbeMatch[i].Scopes->__item =(char *)soap_malloc(soap, 1024);
		memset(ProbeMatches.ProbeMatch[i].Scopes->__item,0,sizeof(ProbeMatches.ProbeMatch->Scopes->__item));	
		strcat(ProbeMatches.ProbeMatch[i].Scopes->__item, "onvif://www.onvif.org/type/NetworkVideoTransmitter");
		ProbeMatches.ProbeMatch[i].Scopes->MatchBy = NULL;

		//ws-discovery¹æ¶¨ Îª¿ÉÑ¡Ïî , ReferenceProperties
		ProbeMatches.ProbeMatch[i].wsa__EndpointReference.ReferenceProperties = 
			(struct wsa__ReferencePropertiesType*)soap_malloc(soap,sizeof(struct wsa__ReferencePropertiesType));
		ProbeMatches.ProbeMatch[i].wsa__EndpointReference.ReferenceProperties->__size = 0;
		ProbeMatches.ProbeMatch[i].wsa__EndpointReference.ReferenceProperties->__any = NULL;
		//ws-discovery¹æ¶¨ Îª¿ÉÑ¡Ïî , ReferenceParameters
		ProbeMatches.ProbeMatch[i].wsa__EndpointReference.ReferenceParameters = 
			(struct wsa__ReferenceParametersType*)soap_malloc(soap,sizeof(struct wsa__ReferenceParametersType));
		ProbeMatches.ProbeMatch[i].wsa__EndpointReference.ReferenceParameters->__size = 0;
		ProbeMatches.ProbeMatch[i].wsa__EndpointReference.ReferenceParameters->__any = NULL;
		//ws-discovery¹æ¶¨ Îª¿ÉÑ¡Ïî , PortType
		ProbeMatches.ProbeMatch[i].wsa__EndpointReference.PortType = 
			(char **)soap_malloc(soap, sizeof(char*) * SMALL_INFO_LENGTH);
		ProbeMatches.ProbeMatch[i].wsa__EndpointReference.PortType[0] = 
			(char *)soap_malloc(soap, sizeof(char) * SMALL_INFO_LENGTH);
		strcpy(ProbeMatches.ProbeMatch[i].wsa__EndpointReference.PortType[0], "ttl");
		//ws-discovery¹æ¶¨ Îª¿ÉÑ¡Ïî , ServiceName
		ProbeMatches.ProbeMatch[i].wsa__EndpointReference.ServiceName = 
			(struct wsa__ServiceNameType*)soap_malloc(soap,sizeof(struct wsa__ServiceNameType));
		ProbeMatches.ProbeMatch[i].wsa__EndpointReference.ServiceName->__item = NULL;
		ProbeMatches.ProbeMatch[i].wsa__EndpointReference.ServiceName->PortName = NULL;
		ProbeMatches.ProbeMatch[i].wsa__EndpointReference.ServiceName->__anyAttribute = NULL;
		//ws-discovery¹æ¶¨ Îª¿ÉÑ¡Ïî , __any
		ProbeMatches.ProbeMatch[i].wsa__EndpointReference.__any = 
			(char **)soap_malloc(soap, sizeof(char*) * SMALL_INFO_LENGTH);
		ProbeMatches.ProbeMatch[i].wsa__EndpointReference.__any[0] = 
			(char *)soap_malloc(soap, sizeof(char) * SMALL_INFO_LENGTH);
		strcpy(ProbeMatches.ProbeMatch[i].wsa__EndpointReference.__any[0], "Any");
		//ws-discovery¹æ¶¨ Îª¿ÉÑ¡Ïî , __anyAttribute
		ProbeMatches.ProbeMatch[i].wsa__EndpointReference.__anyAttribute = 
			(char *)soap_malloc(soap, sizeof(char) * SMALL_INFO_LENGTH);
		strcpy(ProbeMatches.ProbeMatch[i].wsa__EndpointReference.__anyAttribute, "Attribute");
		ProbeMatches.ProbeMatch[i].wsa__EndpointReference.__size = 0;
		//ws-discovery¹æ¶¨ Îª¿ÉÑ¡Ïî , Address
		ProbeMatches.ProbeMatch[i].wsa__EndpointReference.Address = (char *)soap_malloc(soap, sizeof(char) * INFO_LENGTH);
		strcpy(ProbeMatches.ProbeMatch[i].wsa__EndpointReference.Address, _HwId);
	}

	if( soap->header == 0 )	{
		soap->header = (::SOAP_ENV__Header*)soap_malloc(soap, sizeof(struct SOAP_ENV__Header));
		soap->header->wsa__RelatesTo = (::wsa__Relationship*)soap_malloc(soap, sizeof(struct wsa__Relationship));
		//it's here
		soap->header->wsa__MessageID =(char *)soap_malloc(soap, sizeof(char) * INFO_LENGTH);
		strcpy(soap->header->wsa__MessageID,_HwId+4);
		soap->header->wsa__RelatesTo->__item = soap->header->wsa__MessageID;
		soap->header->wsa__RelatesTo->RelationshipType = NULL;
		soap->header->wsa__RelatesTo->__anyAttribute = NULL;
	}
	else {
		soap->header->wsa__RelatesTo = (::wsa__Relationship*)soap_malloc(soap, sizeof(struct wsa__Relationship));
		//it's here
		soap->header->wsa__RelatesTo->__item = soap->header->wsa__MessageID;
		soap->header->wsa__RelatesTo->RelationshipType = NULL;
		soap->header->wsa__RelatesTo->__anyAttribute = NULL;

		soap->header->wsa__MessageID =(char *)soap_malloc(soap, sizeof(char) * INFO_LENGTH);
		strcpy(soap->header->wsa__MessageID,_HwId+4);
	}

	soap->header->wsa__From = 0;
	soap->header->wsa__ReplyTo = 0;
	soap->header->wsa__FaultTo = 0;
	soap->header->wsdd__AppSequence = 0;
	soap->header->wsa__To = (char*)soap_malloc(soap, 128);
	strcpy( soap->header->wsa__To , "http://schemas.xmlsoap.org/ws/2004/08/addressing/role/anonymous");
	soap->header->wsa__Action = (char*)soap_malloc(soap, 128);
	strcpy(soap->header->wsa__Action , "http://schemas.xmlsoap.org/ws/2005/04/discovery/ProbeMatches");

	/* send over current socket as HTTP OK response: */
	soap_send___wsdd__ProbeMatches(soap, "http://", NULL, &ProbeMatches);
	return SOAP_OK;
}


SOAP_FMAC5 int SOAP_FMAC6 __wsdd__ProbeMatches(struct soap*, struct wsdd__ProbeMatchesType *wsdd__ProbeMatches)
{
	fprintf(stderr, "%s: calling ...\n", __func__);

	return -1;
}


SOAP_FMAC5 int SOAP_FMAC6 __wsdd__Resolve(struct soap*, struct wsdd__ResolveType *wsdd__Resolve)
{
	fprintf(stderr, "%s: calling ...\n", __func__);

	return -1;
}


SOAP_FMAC5 int SOAP_FMAC6 __wsdd__ResolveMatches(struct soap*, struct wsdd__ResolveMatchesType *wsdd__ResolveMatches)
{
	fprintf(stderr, "%s: calling ...\n", __func__);

	return -1;
}


SOAP_FMAC5 int SOAP_FMAC6 __ns1__Hello(struct soap*, struct wsdd__HelloType tdn__Hello, struct wsdd__ResolveType &tdn__HelloResponse)
{
	fprintf(stderr, "%s: calling ...\n", __func__);

	return -1;
}


SOAP_FMAC5 int SOAP_FMAC6 __ns1__Bye(struct soap*, struct wsdd__ByeType tdn__Bye, struct wsdd__ResolveType &tdn__ByeResponse)
{
	fprintf(stderr, "%s: calling ...\n", __func__);

	return -1;
}


SOAP_FMAC5 int SOAP_FMAC6 __ns2__Probe(struct soap*, struct wsdd__ProbeType tdn__Probe, struct wsdd__ProbeMatchesType &tdn__ProbeResponse)
{
	fprintf(stderr, "%s: calling ...\n", __func__);

	return -1;
}

SOAP_FMAC5 int SOAP_FMAC6 __tdn__Hello(struct soap*, struct wsdd__HelloType tdn__Hello, struct wsdd__ResolveType &tdn__HelloResponse)
{
	fprintf(stderr, "%s: calling ...\n", __func__);

	return -1;
}

SOAP_FMAC5 int SOAP_FMAC6 __tdn__Bye(struct soap*, struct wsdd__ByeType tdn__Bye, struct wsdd__ResolveType &tdn__ByeResponse)
{
	fprintf(stderr, "%s: calling ...\n", __func__);

	return -1;
}

SOAP_FMAC5 int SOAP_FMAC6 __tdn__Probe(struct soap*, struct wsdd__ProbeType tdn__Probe, struct wsdd__ProbeMatchesType &tdn__ProbeResponse)
{
	fprintf(stderr, "%s: calling ...\n", __func__);

	return -1;
}


SOAP_FMAC5 int SOAP_FMAC6 SOAP_ENV__Fault(struct soap*, char *faultcode, char *faultstring, char *faultactor, struct SOAP_ENV__Detail *detail, struct SOAP_ENV__Code *SOAP_ENV__Code, struct SOAP_ENV__Reason *SOAP_ENV__Reason, char *SOAP_ENV__Node, char *SOAP_ENV__Role, struct SOAP_ENV__Detail *SOAP_ENV__Detail)
{
	return -1;
}


