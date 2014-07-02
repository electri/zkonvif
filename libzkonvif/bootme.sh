#!/bin/bash

if [ -z $GSOAP ]; then
	GSOAP=/usr/share/gsoap
fi

if [ ! -f $GSOAP/import/stl.h ]; then
	echo "ERR: give me yr gsoap path!!!"
	exit
fi


if [ ! -f zonvif.h ]; then
	wsdl2h.exe -jPt wsdl/typemap.dat wsdl/event.wsdl wsdl/devicemgmt.wsdl wsdl/remotediscovery.wsdl wsdl/ptz.wsdl -o zonvif0.h
	echo '#import "wsse.h"' > zonvif.h
	cat zonvif0.h >> zonvif.h
	dos2unix zonvif.h
	rm -f zonvif0.h
fi

rm -fr soap/
mkdir -p soap/xml

soapcpp2 -2jLd soap/ zonvif.h -I${GSOAP}:${GSOAP}/import
mv soap/*.xml soap/xml/

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
