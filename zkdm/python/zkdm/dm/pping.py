#!/usr/bin/python
# coding: utf-8
#
# @file: pping.py
# @date: 2014-12-31
# @brief:
# @detail:
#
#################################################################


from DbOp import *
import socket
sys.path.append('../common')
import uty_token
import select, time
import os 

TARGET_PORT = 11011


def _send_pings(fd, ips):
    ''' TODO: 可以考虑在线的，60秒发一次，不在线的 10秒一次,
        windows 上遇到一个操蛋的问题, 当给不存在的 ip 执行 sendto, 则下次 recvfrom会返回 10054 
        错误, 所以 sendto 时都是临时创建 socket 吧:
    '''
    fd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    for ip in ips:
        print 'send ping to:', ip
        fd.sendto('ping', (ip, TARGET_PORT))
    fd.close()

def ping_all(fname):
    ''' fname 为 tokens.json '''
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    ips = db_init_from_tokens(fname)
    print ips

    last_send_ping = 0
    while True:
        rc = select.select([sock], [], [], 10)

        if len(rc[0]) == 0: # timeout, just 
            _send_pings(sock, ips)
            db_check_timeout(time.time())
            last_send_ping = time.time()

        elif len(rc[0]) > 0: # 能收到 pong 了
            pong, remote = sock.recvfrom(16)
            if pong == 'pong':
                remote_ip = remote[0]
                print 'update:', remote_ip
                db_update(remote_ip)

            t = time.time()
            if t - last_send_ping > 10:
                _send_pings(sock, ips)
                db_check_timeout(t)
                last_send_ping = t


if __name__ == '__main__':
    ping_all('../common/tokens.json')



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

