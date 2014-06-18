#!/bin/bash

# 生成自签名证书 ca-cert 

if [ -f ca-cert.pem ]; then
	echo 'ca-cert exist ...'
else
	openssl req -x509 -newkey rsa:2048 -keyout ca-pri.key -out ca-cert.pem -days 3650 -nodes
	openssl x509 -outform der -in ca-cert.pem -out ca-cert.crt
fi

# 生成 server 端证书，使用ca-cert 签名 ...

if [ -f server.pem ]; then
	echo 'server.pem exist ...'
else
	openssl req -new -newkey rsa:2048 -keyout server.key -out server.req -nodes
	openssl x509 -req -days 365 -in server.req \
		-CA ca-cert.pem -CAkey ca-pri.key -CAcreateserial \
		-out server.crt

	echo "== server cert ==" > server.pem
	cat server.crt >> server.pem
	echo "== server pri key ==" > server.pem
	cat server.key >> server.pem
	echo "== ca cert ==" >> server.pem
	cat ca-cert.pem >> server.pem
fi

