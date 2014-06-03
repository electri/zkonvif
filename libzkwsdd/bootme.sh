#!/bin/bash

if [ -z $GSOAP ]; then
	GSOAP=/usr/share/gsoap
fi

wsdl2h -jP -Nwsdd -o wsdd.h wsdl/remotediscovery.wsdl
soapcpp2 -jL -d soap/ -I $GSOAP/import wsdd.h

