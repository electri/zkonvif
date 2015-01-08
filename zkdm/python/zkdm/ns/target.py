#!/usr/bin/python
# coding: utf-8
#
# @file: target.py
# @date: 2015-01-08
# @brief: 对来自 Target 的组播包进行解析
# @detail:
#
#################################################################


def parse_target_descr(info):
    '''
        target 组播自己的主机信息和服务信息，每行一条，定义如下：

        # 为注释行
        # mac 地址，linux下可以使用 cat /sys/class/net/eth0/address | sed s/://g 生成
        mac=xxxx
        # host type 目前可能 jp100hd, jp100dgl, 3100, 2200 ....
        hosttype=3100
        # 以下为服务描述，每个 stype 将说明启动一个新的服务描述
        stype=ptz
        # 服务id
        id=teacher
        # 本服务实例私有描述，等号后，可以包含随意信息，但不能包含 \n
        private=port:3366;protocol=tcp;...
        # 新的服务实例开始了
        stype=ptz
        id=student
        private=port:3366;protocol=tcp;...
        # 另一种服务类型
        stype=recording
        id=recording
        private=....
        ....
        
        以上 mac, hosttype, stype, id, private 字段必须都包含

        返回字典描述格式:

            {
                "mac": xxx,
                "hosttype": xxx,

                "services": [
                    { 'type': 'ptz', 'id': 'teacher', 'private': 'xx' },
                    { 'type': 'ptz', 'id': 'student', 'private': 'xx' },
                    { 'type': 'recording', 'id': 'recording', 'private': 'xx' },
                ]
            }
    '''
    st = "h"
    hdescr = {'services':[]}
    s = {}

    lines = info.split('\n')
    for line in lines:
        line = line.strip()
        if len(line) < 3:
            continue
        if line[0] == '#':
            continue

        kvs = line.split('=', 2)
        if len(kvs) != 2:
            continue

        if st == 'h': # 解析 host
            if kvs[0] == 'stype':
                st = 's'
                if 'type' in s and 'id' in s and 'private' in s: # service 有效
                    hdescr['services'].append(s)

                s = {}
                s['type'] = kvs[1]
            else:
                hdescr[kvs[0]] = kvs[1]
        elif st == 's': # 解析 service
            if kvs[0] == 'stype':
                st = 's'
                if 'type' in s and 'id' in s and 'private' in s: # service 有效
                    hdescr['services'].append(s)

                s = {}
                s['type'] = kvs[1]
            else:
                s[kvs[0]] = kvs[1]
    # 别忘了检查最好一个

            

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

