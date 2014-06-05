#include "soapH.h"
#include "../soap/wsdd.nsmap"

int SOAP_ENV__Fault(struct soap*, char *faultcode, char *faultstring, char *faultactor, 
					struct SOAP_ENV__Detail *detail, struct SOAP_ENV__Code *SOAP_ENV__Code, 
					struct SOAP_ENV__Reason *SOAP_ENV__Reason, char *SOAP_ENV__Node, 
					char *SOAP_ENV__Role, struct SOAP_ENV__Detail *SOAP_ENV__Detail)
{
	return SOAP_OK;
}
