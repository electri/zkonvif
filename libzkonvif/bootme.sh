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
	wsdl2h -vjP -o onvif0.h -t wsdl/typemap.dat \
		http://www.onvif.org/onvif/ver10/event/wsdl/event.wsdl	\
		http://www.onvif.org/onvif/ver10/device/wsdl/devicemgmt.wsdl \
		http://www.onvif.org/onvif/ver20/ptz/wsdl/ptz.wsdl \
		http://www.onvif.org/onvif/ver10/network/wsdl/remotediscovery.wsdl
	echo '#import "wsse.h"' > onvif.h
	cat onvif0.h >> onvif.h
	rm -f onvif0.h

fi

if [ -f onvif2.h ]; then
	echo 'onvif2.h exist!'
else
	wsdl2h -vgdy -o onvif2.h -t wsdl/typemap.dat -r127.0.0.1:8087 \
	       'http://www.onvif.org/onvif/ver10/event/wsdl/event.wsdl' \
	       'http://www.onvif.org/onvif/ver10/device/wsdl/devicemgmt.wsdl' \
	       'http://www.onvif.org/onvif/ver20/ptz/wsdl/ptz.wsdl' \
	       'http://www.onvif.org/onvif/ver10/network/wsdl/remotediscovery.wsdl'
	       if [ $? -eq 0 ]; then
			echo 'OK'
	       else
		       echo 'wsdl2h err ...'
	       fi
fi
     

exit

# 貌似 wsa5.h 中 SOAP_ENV__Fault 重复定义
if [ -f wsa5.h ]; then
	echo 'wsa5.h exist!'
else
	cp $GSOAP/import/wsa5.h .
	sed -i 's/int SOAP_ENV__Fault/int SOAP_ENV__Fault2/g' wsa5.h
fi

rm -rf soap/*

mkdir -p soap/xml/
mkdir -p soap/wsdl/

soapcpp2 -2jLd soap/ onvif.h -I.:$GSOAP/import:$GSOAP
mv -f soap/*.xml soap/xml
mv -f soap/*.wsdl soap/wsdl
mv -f soap/*.xsd soap/wsdl

cp gsoap/* soap/
cp $GSOAP/custom/duration.c soap/duration.cpp
cp $GSOAP/custom/duration.h soap/
cp $GSOAP/plugin/threads.c soap/threads.cpp
cp $GSOAP/plugin/threads.h soap/
cp $GSOAP/plugin/wsaapi.h soap/
cp $GSOAP/plugin/wsaapi.c soap/wsaapi.cpp
cp $GSOAP/plugin/wsseapi.h soap/
cp $GSOAP/plugin/wsseapi.c soap/wsseapi.cpp
cp $GSOAP/plugin/mecevp.h soap/
cp $GSOAP/plugin/mecevp.c soap/mecevp.cpp
cp $GSOAP/plugin/smdevp.h soap/
cp $GSOAP/plugin/smdevp.c soap/smdevp.cpp


echo '#include "wsdd.nsmap"' > soap/nsmap.cpp

echo 'En, just make it!'
