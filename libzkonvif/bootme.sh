#!/bin/sh

# 修改 GSOAP 的路径 ...
if [ -z $GSOAP ]; then
	GSOAP=/usr/share/gsoap
fi

if [ -f onvif.h ]; then
	echo 'onvif.h exist!'
else
	echo 'exec wsdl2h ...'
	wsdl2h -vjP -o onvif.h -t wsdl/typemap.dat \
		wsdl/devicemgmt.wsdl \
		wsdl/deviceio.wsdl \
		wsdl/event.wsdl \
		wsdl/media.wsdl \
		wsdl/remotediscovery.wsdl
fi

# 貌似 wsa5.h 中 SOAP_ENV__Fault 重复定义
if [ -f wsa5.h ]; then
	echo 'wsa5.h exist!'
else
	cp $GSOAP/import/wsa5.h .
	sed -i 's/int SOAP_ENV__Fault/int SOAP_ENV__Fault2/g' wsa5.h
fi

rm -rf soap/*

mkdir -p soap/xml/

soapcpp2 -jLd soap/ onvif.h -I.:$GSOAP/import:$GSOAP
mv soap/*.xml soap/xml

echo '#include "wsdd.nsmap"' > soap/nsmap.cpp

echo 'En, just make it!'
