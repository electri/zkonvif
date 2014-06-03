#include <stdio.h>
#include "soapH.h"
#include "wsdd.nsmap"


bool create_server_socket_udp(int& server_udp);
int send_hello();
struct soap *soap_udp;

int main()
{
	printf("start \n");  
	int server_udp;
	int retval=0;

	
	int fault_flag=0;

	if(create_server_socket_udp(server_udp)==false)
	{
		return -1;
	}

	soap_udp=soap_new();

	soap_init1(soap_udp,SOAP_IO_UDP);

	soap_udp->master = server_udp;
	soap_udp->socket = server_udp;
	soap_udp->errmode = 0;
	soap_udp->bind_flags = 1;
	soap_udp->ipv4_multicast_ttl = 1;

	send_hello();

	while(1)
	{
		retval=soap_serve(soap_udp);

		if(retval&&!(fault_flag))
		{
			fault_flag=1;
		}
		else if(!retval)
		{
			fault_flag=0;
		}

		soap_destroy(soap_udp);
		soap_end(soap_udp);
	}


	soap_done(soap_udp);

	soap_free(soap_udp);

	return 0;
}



int send_hello()
{
    struct soap *soap;
    soap=soap_new1(SOAP_IO_UDP);
    soap_init1(soap,SOAP_IO_UDP);
    
    struct wsdd__HelloType *wsdd__Hello = NULL;
    
	const char *soap_endpoint=soap_strdup(soap,"urn:uuid:D149F919-4013-437E-B480-3707D96D27A4");
	const char *soap_action= soap_strdup(soap,"http://docs.oasis-open.org/ws-dd/ns/discovery/2009/01/Hello");

	wsdd__Hello=(struct wsdd__HelloType *) soap_malloc(soap, sizeof(struct wsdd__HelloType));

	wsdd__Hello->wsa__EndpointReference.Address = soap_strdup(soap,"urn:uuid:D149F919-4013-437E-B480-3707D96D27A4");
	//wsdd__Hello->Types = ;
	//wsdd__Hello->Scopes->MatchBy = ;
	//wsdd__Hello->Scopes->__item = ;
	//wsdd__Hello->XAddrs = ;
	wsdd__Hello->MetadataVersion = 10086;

	SOAP_FMAC6 soap_send___wsdd__Hello(soap,soap_endpoint,soap_action,wsdd__Hello);
	
    return 0;
}

bool  create_server_socket_udp(int& server_udp)
{
	unsigned char one=1;
	int sock_opt=1;

	server_udp=::socket(PF_INET, SOCK_DGRAM, IPPROTO_UDP);
	if (server_udp == -1) 
	{
		printf("unable to create socket\n");
		return false;
	}
	
	/* reuse socket addr */
	if ((setsockopt(server_udp, SOL_SOCKET, SO_REUSEADDR, (const char *) &sock_opt,sizeof (sock_opt))) == -1) 
	{
		return false;
	}

	// Multi-cast
	//if ((setsockopt(server_udp, IPPROTO_IP, IP_MULTICAST_LOOP,(const char*) &one, sizeof (unsigned char))) == -1)
	//{
	//	return false;
	//}
	
	struct ip_mreq mreq;
	mreq.imr_multiaddr.s_addr = inet_addr("239.255.255.250");
	mreq.imr_interface.s_addr = htonl(INADDR_ANY);

	if(setsockopt(server_udp,IPPROTO_IP,IP_ADD_MEMBERSHIP,(const char*)&mreq,sizeof(mreq))==-1)
	{
		return false;
	}

	// previous soap binding
	struct sockaddr_in local_addr;
	memset(&local_addr,0,sizeof(local_addr));
	local_addr.sin_family = AF_INET;
	local_addr.sin_addr.s_addr = htonl(INADDR_ANY);
	local_addr.sin_port = htons(3702);
	bind(server_udp,(struct sockaddr*)&local_addr,sizeof(local_addr));
	return true;
}
