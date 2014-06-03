#!/bin/bash

if [ -z $GSOAP ]; then
	GSOAP=/usr/share/gsoap
fi

wsdl2h -jP -o wsdd.h wsdl/remotediscovery.wsdl
soapcpp2 -L -d soap/ -I $GSOAP/import wsdd.h

