#!/usr/bin/python
# coding: utf-8
#
# @file: pping.py
# @date: 2015-01-08
# @brief:
# @detail: 对照实现 ping.c 中的逻辑
#
#################################################################


from socket import *
import select, struct, time
import dbhlp as db


MCAST_ADDR = "239.10.10.7"
MCAST_PORT = 11012


def __open_socks():
    ''' 创建两个 socket, 一个用于发送ping，接收 pong,
        另一个加入组播地址，接收 target 组播信息
    '''
    s0 = socket(AF_INET, SOCK_DGRAM)
    s1 = socket(AF_INET, SOCK_DGRAM)

    # non-blocking
    s0.setblocking(0)
    s1.setblocking(0)

    # bind
    s1.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s1.bind(('', MCAST_PORT))

    # join multicast
    mreq = struct.pack('4sl', inet_aton(MCAST_ADDR), INADDR_ANY)
    s1.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, mreq)

    return s0, s1


def __recv_pong(s):
    ''' 从 s 接收 pong 消息 '''
    try:
        data, addr = s.recvfrom(16)
        if data[0:4] == 'pong':
            target_ip = addr[0]
            db.update_target_pong(time.time(), target_ip)
    except:
        pass

    return -1


def __parse_mcast(info, ip):
    ''' 收到来自 target 的主机/服务描述,

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
    '''
    # TODO: 实现上述解析，同时要考虑 target 端配置起来是否复杂？
    pass


def __recv_mcast(s):
    ''' 收到组播信息 '''
    try:
        data, addr = s.recvfrom(4096)
        # 前5个字节，必须是 pong\n
        if data[0:5] == 'pong\n':
            __parse_mcast(data[6:], addr[0])
            print data[6:]
    except:
        pass
    return 0


def __chk_timeout():
    ''' 检查超时主机，如果超时，则所有对应的服务都设置为 offline '''
    db.chk_timeout(time.time())
    return 0


def __send_pings(s, force):
    ''' 发送 pings '''
    ips= db.get_targets_ip(online=force)
    for ip in ips:
        s.sendto('ping', (ip, 11011))
    return 0


def __main():
    ''' 主过程 ... '''
    s0, s1 = __open_socks()
    last_stamp_poff = time.time() # 上次发送ping给所有非在线 target 的时间
    last_stamp_pf = time.time() # 上次强制发送 ping 的时间
    last_chk_time = time.time() # 上次检查超时的时间

    while True:
        r,w,e = select.select([s0, s1], [], [], 10.0)
        print r
        if s0 in r:
            __recv_pong(s0)

        if s1 in r:
            __recv_mcast(s1)
        
        t = time.time()
        if t - last_stamp_pf > 60:
            __send_pings(s0, True)

        elif t - last_stamp_poff > 10:
            __send_pings(s0, False)

        __chk_timeout()


if __name__ == '__main__':
    __main()


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

