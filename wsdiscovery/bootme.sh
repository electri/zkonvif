#!/bin/sh

if [ -z $GSOAP ]; then
	GSOAP=/usr/share/gsoap
fi

if [ -f onvif.h ]; then
	echo 'onvif.h exist!'
else
	wsdl2h -o onvif.h -P -t ./typemap.dat http://www.onvif.org/onvif/ver10/network/wsdl/remotediscovery.wsdl
fi

soapcpp2 -L onvif.h -I$GSOAP/import


echo 'En, just make it!'
