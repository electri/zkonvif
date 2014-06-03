#!/bin/sh

# 修改 GSOAP 的路径 ...
if [ -z $GSOAP ]; then
	GSOAP=/usr/share/gsoap
fi

if [ -f onvif.h ]; then
	echo 'onvif.h exist!'
else
	wsdl2h.exe -jP -oonvif.h -t soap/typemap.dat \
		wsdl/devicemgmt.wsdl \
		wsdl/deviceio.wsdl \
		wsdl/event.wsdl \
		wsdl/media.wsdl \
		wsdl/remotediscovery.wsdl
fi

mkdir -p soap

# 貌似 wsa5.h 中 SOAP_ENV__Fault 重复定义
if [ -f wsa5.h ]; then
	echo 'wsa5.h exist!'
else
	cp $GSOAP/import/wsa5.h .
	sed -i 's/int SOAP_ENV__Fault/int SOAP_ENV__Fault2/g' wsa5.h
fi

soapcpp2.exe -Ld soap/ onvif.h -I.:/usr/share/gsoap/import:/usr/share/gsoap

echo 'En, just make it!'
