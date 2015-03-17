#!/usr/bin/python
# coding: utf-8
#
# @file: conf_srv.py
# @date: 2015-03-05
# @brief:
# @detail: 通过组播发布配置
#
#################################################################


import socket, struct, select, json, io


CONF_FNAME = 'global_conf.json' # 需要发布的配置
MC_ADDR = '239.10.123.7'
LS_PORT = 9707
REQ = 'getconf' # 获取全局配置的命令字符串


def __load_conf():
    ''' 加载本地配置文件 '''
    ret = json.load(io.open(CONF_FNAME, 'r', encoding='utf-8'))
    return json.dumps(ret)


def __reload_conf(s):
    try:
        ret = json.load(io.open(CONF_FNAME, 'r', encoding='utf-8'))
        return json.dumps(ret)
    except:
        print 'ERR: parse %s fault!' % CONF_FNAME
        return s


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
mreq = struct.pack('=4sl', socket.inet_aton(MC_ADDR), socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
sock.bind(('0.0.0.0', LS_PORT))

print 'INFO: server started, bind port %d' % LS_PORT

try:
    conf = __load_conf()
except:
    print 'ERR: parse %s fault!' % CONF_FNAME
    sys.exit()

while True:
    ins, outs, errs = select.select([sock], [], [], 10.0)
    for r in ins:
        try:
            data, addr = sock.recvfrom(65536)
            print 'INFO:', addr, data
        except:
            continue
        
        if data == REQ:
            conf = __reload_conf(conf)
            sock.sendto(conf, addr)





# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

