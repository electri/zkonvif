#!/usr/bin/python
# coding: utf-8
#
# @file: boot.py
# @date: 2015-03-05
# @brief:
# @detail: 通过组播形式,更新全局配置
#
#################################################################

import socket, select, json, os, io


MC_ADDR = '239.10.123.7'
LS_PORT = 9707
REQ = 'getconf' # 获取全局配置的命令字符串


def getconf_mulcast():
    ''' 向周知的组播地址发送请求,等待3秒,如果收到配置,则返回,否则返回缺省配置 
        返回的配置项, 使用 json.loads() 加载解析 ...
    '''
    if os.getenv('zonekey_mc', '1') == '0':
        return __def_conf()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(0) # 设置非阻塞
        
    sock.sendto(REQ, (MC_ADDR, LS_PORT))

    ins, outs, errs = select.select([sock], [], [], 3) # 三秒内收到
    if len(ins) == 1:
        try:
            data, addr = sock.recvfrom(65536)
        except:
            sock.close()
            return __def_conf()
        else:
            # 返回 data 作为配置信息
            sock.close()
            return data
    else:
        return __def_conf()


def __def_conf():
    ''' 返回缺省配置信息
        现在的配置信息就是平台服务的吧
    '''
    abspath = os.path.abspath(__file__)
    hosts_config_fname = os.path.dirname(abspath) + "/global_conf.json"
    try:
        ret = json.load(io.open(hosts_config_fname, 'r', encoding='utf-8'))
        return json.dumps(ret)
    except:
        gc = { "NSService": { "sip" : "172.16.30.251", "sport" :"8080" }}
        return json.dumps(gc)



if __name__ == '__main__':
    conf = getconf_mulcast()
    c = json.loads(conf)

    print '版本描述:', c['AutoUpdate']['version']
    print '更新包:', c['AutoUpdate']['package']


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

