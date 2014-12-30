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

hds =  uty_token.gather_hds('../common/tokens.json');
hips = []
for hd in hds:
    hips.append(hd['ip'])
    
db = DbOp.DbOp('proxied_hosts.db')
db.emptyTable('hosts_state')
#key: ip, value {islive, timestamp}
temps = {}
for hip in hips:
    print hip
    temps.update({str(hip):{'isLive':0, 'timesstamp':None}})
print temps    
for hip in hips:
#FIXME:崩溃,往表里面不能插入 unicode
    db.insertTable('hosts_state', (str(hip), 0))

db.close()
    
address = ('127.0.0.1', 31500)
sock = socket.socket(AF_INT, SOCK_DGRAM)
sock.bind(address)

db = DbOp('Proxied_hosts.db')

while True:
    result = select.select([sock], [], [], 10)
    if result == 0:
        for e in temps:
            if temps[e].isLive = 1:
                now = datetime.datetime.now()
                if now - temps[e].timestamp > 20
                    temps[e].isLive = 0;
                    db = dbop.dbop('proxied_hosts')
                    db.altervalue('hosts_state', (str(e), 0))
                    db.close()
            if temps[e].isLive = 0:
                sock.sendto('ping', (e, 222))
    else if result == -1:
        print 'error'
    else:
        data, address = sock.recvfrom(10)
        now = datetime.datetime.now()
        if data == 'pang':
            e = address[0]
            if temps[e].isLive == 0:
                temps[e].isLive = 1 
                db = DbOp.DbOp('proxied_hosts')
                db.alterValue('hosts_state', (str(e), 1))
                db.close()
            if temps[e].isLive == 1:
                temps[e].timeStamp = now

 vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

