# coding: utf-8
# @file: ping.py
# @date: 2014-12-30
# @brief:
# @detail:
#
#################################################################
import json
import DbOp
import socket
import os,sys
sys.path.append('../common')
import uty_token
import datetime
import select

PORT = 2222
TOTAL_TIME_STAMP = 60
PING_TIME_STAMP = 10
PONG_TIME_STAMP = 15
temps = DbOp.loadFile('../common/tokens.json');
#key: ip, value {islive, timestamp}
    
# XXX: 这里为什么要绑定？而且还绑定了 localhost?
#      如果绑定了 localhost,则只能接收到 localhost 发送的数据
#      当 socket 没有绑定 port 时，会在第一次调用 sendto/send 时
#      自己绑定一个未被占用的端口
#address = ('127.0.0.1', 31500)
sock = socket.socket(AF_INT, SOCK_DGRAM)
#sock.bind(address)

total_last_time = datetime.datetime.now()

while True:
    now = datetime.datetime.now()
    if (now - total_last_time > TOTAL_TIME_STAMP:
        for e in temps:
            sock.sendto('ping', (e, PORT)) 
            total_last_time = now

    result = select.select([sock], [], [], PING_TIME_STAMP)
    if result == 0:
        for e in temps:
            if temps[e].isLive = 1:
                now = datetime.datetime.now()
                if (now - temps[e].timeStamp).seconds > PONG_TIME_STAMP
                    temps[e].isLive = 0;
                    DbOp.alterTableValue((str(e), 0))
            if temps[e].isLive = 0:
                sock.sendto('ping', (e, PORT))
    else if result == -1:
        print 'error'
        continue
    else:
        data, address = sock.recvfrom(10)
        now = datetime.datetime.now()
        if data == 'pang':
            e = address[0]
            if temps[e].isLive == 0:
                temps[e].isLive = 1 
                DbOp.alterTableValue((str(e), 1))
            if temps[e].isLive == 1:
                temps[e].timeStamp = now

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

