#!/bin/bash

if [ -z $GSOAP ]; then
	GSOAP=/usr/share/gsoap
fi

if [ ! -f $GSOAP/import/stl.h ]; then
	echo "ERR: give me yr gsoap path!!!"
	exit
fi


if [ ! -f zonvif.h ]; then
	wsdl2h.exe -jPt wsdl/typemap.dat wsdl/event.wsdl wsdl/devicemgmt.wsdl wsdl/remotediscovery.wsdl wsdl/ptz.wsdl -o zonvif.h
fi

rm -fr soap/
mkdir -p soap/xml

soapcpp2 -2jLd soap/ zonvif.h -I${GSOAP}:${GSOAP}/import
mv soap/*.xml soap/xml/
