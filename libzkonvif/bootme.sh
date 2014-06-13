#!/bin/sh

# 修改 GSOAP 的路径 ...
if [ -z $GSOAP ]; then
	GSOAP=/usr/share/gsoap
fi

if [ -f onvif.h ]; then
	echo 'onvif.h exist!'
else
	echo 'exec wsdl2h ...'
#v: verbose output; j: don't generate SOAP_ENV__HEADER and SOAP_ENV__Detail 
#definitions; p: don't create polymorphic types inherited from xsd__anyType
	wsdl2h -vjP -o onvif.h -t wsdl/typemap.dat \
		http://www.onvif.org/onvif/ver10/event/wsdl/event.wsdl	\
		http://www.onvif.org/onvif/ver10/device/wsdl/devicemgmt.wsdl \
		http://www.onvif.org/onvif/ver20/ptz/wsdl/ptz.wsdl \
		http://www.onvif.org/onvif/ver10/network/wsdl/remotediscovery.wsdl
#http://www.onvif.org/onvif/ver10/deviceio.wsdl
#http://www.onvif.org/onvif/ver20/analytics/wsdl/analytics.wsdl
#http://www.onvif.org/onvif/ver10/analyticsdevice.wsdl
#http://www.onvif.org/onvif/ver10/display.wsdl
#http://www.onvif.org/onvif/ver20/imaging/wsdl/imaging.wsdl
#http://www.onvif.org/onvif/ver10/media/wsdl/media.wsdl
#http://www.onvif.org/onvif/ver10/Receiver.wsdl
#http://www.onvif.org/onvif/ver10/Recording.wsdl
#http://www.onvif.org/onvif/ver10/Replay.wsdl
#http://www.onvif.org/onvif/ver10/Search.wsdl

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
cp gsoap/* soap/
cp $GSOAP/custom/duration.c soap/duration.cpp
cp $GSOAP/custom/duration.h soap/

echo '#include "wsdd.nsmap"' > soap/nsmap.cpp

echo 'En, just make it!'
