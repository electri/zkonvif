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
import target


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


def __recv_pong(s, now):
    ''' 从 s 接收 pong 消息 '''
    try:
        data, addr = s.recvfrom(16)
        if data[0:4] == 'pong':
            target_ip = addr[0]
            db.update_target_pong(now, target_ip)
            print 'got PONG from:', addr[0]
    except Exception as e:
        print 'EXCEPT: __recv_pong:', e

    return 0


def __recv_mcast(s):
    ''' 收到组播信息 '''
    try:
        data, addr = s.recvfrom(4096)
        # 前5个字节，必须是 pong\n
        if data[0:5] == 'pong\n':
            info = data[5:]
            tdescr = target.parse_target_descr(info)
            if 'mac' in tdescr:
                tdescr['ip'] = addr[0]
                db.update_target_descr(tdescr)
                print 'INFO: update mcast info from:', addr[0]
                return True, addr

    except Exception as e:
        print 'EXCEPT: __recv_mcast: ', e
    return False, addr


def __chk_timeout(now):
    ''' 检查超时主机，如果超时，则所有对应的服务都设置为 offline '''
    db.chk_timeout(now)
    return 0

def __send_ping(s, ip):
    ''' 发送 ping 到 ip '''
    print 'send PING to:', ip
    return s.sendto('ping', (ip, 11011))


def __send_pings(s, force):
    ''' 发送 pings '''
    ips= db.get_targets_ip(online=force)
    for ip in ips:
        __send_ping(s, ip)
    return 0


def __main():
    ''' 主过程 ... '''
    s0, s1 = __open_socks()
    last_stamp_poff = time.time() # 上次发送ping给所有非在线 target 的时间
    last_stamp_pf = time.time() # 上次强制发送 ping 的时间
    last_chk_time = time.time() # 上次检查超时的时间

    while True:
        r,w,e = select.select([s0, s1], [], [], 10.0)
        t = time.time()
        if s0 in r:
            __recv_pong(s0, t)

        if s1 in r:
            success, remote = __recv_mcast(s1)
            if success:
                # 收到合理组播后，立即对其发送 ping
                __send_ping(s0, remote[0])
        
        if t - last_stamp_pf > 60:
            __send_pings(s0, True)
            last_stamp_pf = t
        elif t - last_stamp_poff > 10:
            __send_pings(s0, False)
            last_stamp_poff = t

        __chk_timeout(t)


if __name__ == '__main__':
    __main()


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

