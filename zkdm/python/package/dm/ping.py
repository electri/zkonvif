# coding: utf-8
# @file: ping.py
# @date: 2014-12-30
# @brief:
# @detail:
#
#################################################################
import json
from DbOp import *
import socket
import os,sys
sys.path.append('../common')
import uty_token
import datetime
import select, time


TARGET_PORT = 11011


def _send_pings(fd, ips):
    for ip in ips:
        socket.sendto(fd, 'ping', (ip, TARGET_PORT)


def ping_all(fname):
    ''' fname 为 tokens.json '''
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ips = db_init_from_tokens(fname)

    last_send_ping = 0
    while True:
        rc = socket.select([sock], [], [], 10)
        if len(rc) == 0: # timeout, just 
            _send_pings(sock, ips)
            db_check_timeout(time.time())
            last_send_ping = time.time()

        elif len(rc) > 0: # 能收到 pong 了
            pong, remote = socket.recvfrom(sock, 4)    
            if pong == 'pong':
                remote_ip = remote[0]
                print db_update(remote_ip)

            t = time.time()
            if t - last_send_ping > 10:
                _send_pings(sock, ips)
                db_check_timeout(t)
                last_send_ping = t


            









PORT = 2222
TOTAL_TIME_STAMP = 60
PING_TIME_STAMP = 10
PONG_TIME_STAMP = 15
temps = DbOp.DbLoadFile('../common/tokens.json');
#key: ip, value: {islive, timestamp}
    
# XXX: 这里为什么要绑定？而且还绑定了 localhost?
#      如果绑定了 localhost,则只能接收到 localhost 发送的数据
#      当 socket 没有绑定 port 时，会在第一次调用 sendto/send 时
#      自己绑定一个未被占用的端口
sock = socket.socket(AF_INT, SOCK_DGRAM)

total_last_time = datetime.datetime.now()

while True:
    now = datetime.datetime.now()
    if ((now - total_last_time).times > TOTAL_TIME_STAMP:
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
    elif result == -1:
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
            for e in temps:
                if temps[e].isLive == 0:
                    sock.sendto('ping', (e, PORT))
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

