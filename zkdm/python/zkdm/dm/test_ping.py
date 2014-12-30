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
"""
address = ('127.0.0.1', 31500)
sock = socket.socket(AF_INT, SOCK_DGRAM)
sock.bind(address)

db = DbOp('Proxied_hosts.db')

while True:
    data, addr = s.recvfrom(10)
    if not data:
        print "client has exist"
        break
    print "received:", data, "from", addr
    if data == 'pang':
      state = db.selectByOpt('proxied_host_state', 'ip = %s'%(addr[0]) 
      if state[1] == 0:
          db.alterValue('proxied_host_state', 1)
          t = gettime()
          ip_times.update({'ip', ,
"""
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

