#!/usr/bin/python
# coding: utf-8
#
# @file: dbhlp.py
# @date: 2015-01-08
# @brief: 实现对 ns.db 的操作
# @detail:
#
#################################################################

import sqlite3, time, sys


DB_FNAME = "ns.db"


def __tab_is_exist(c, tabname):
    ''' 返回 tabname 是否存在 '''
    s0 = 'select COUNT(*) from sqlite_master where name="%s"' % (tabname)
    rows = c.execute(s0)
    return int(rows.next()[0]) > 0


def __db_init():
    ''' 检查数据库
    '''
    db = sqlite3.connect(DB_FNAME)
    c = db.cursor()

    if not __tab_is_exist(c, "hosts"):
        s1 = 'create table hosts(mac varchar(64), ip varchar(64), type varchar(16),\
                last_stamp integer)'
        c.execute(s1)

    if not __tab_is_exist(c, "services"):
        s1 = 'create table services(mac varchar(64), ip varchar(64), type varchar(16),\
                id varchar(16), online integer, private varchar(1024))'
        c.execute(s1)

    # 删除没有 hosts 信息的 services
    s2 = 'delete from services where NOT exists (select mac from hosts where mac=services.mac)'
    c.execute(s2)

    # 所有 service online = 0
    s3 = 'update services set online=0'
    c.execute(s3)

    db.commit()
    db.close()


def update_target_pong(stamp, ip):
    ''' 更新 hosts 中，ip 对应的主机的 last_stamp 
        FIXME: 这里有隐患，应该使用 mac 而不是 ip 来索引
        XXX: 哦，select 返回的 result，不能直接在里面执行 cursor 操作 ...
    '''
    db = sqlite3.connect(DB_FNAME)
    c = db.cursor()
    s1 = 'update hosts set last_stamp=%d where ip="%s"' % (stamp, ip)
    c.execute(s1)

    s0 = 'select mac from hosts where ip="%s"' % (ip)
    result = c.execute(s0)

    rs = [r[0] for r in result]

    for mac in rs:
        s1 = 'update services set online=1 where online=0 and mac="%s"' % (mac)
        c.execute(s1)

    db.commit()
    db.close()


def chk_timeout(curr):
    ''' 更新所有 curr - hosts.last_stamp > 10 的主机的所有服务的 online 为 0 '''
    db = sqlite3.connect(DB_FNAME)
    c = db.cursor()
    s0 = 'select mac from hosts where last_stamp + 10 < %d' % (curr)
    result = c.execute(s0)

    rs = [r[0] for r in result]
        
    for mac in rs:
        s1 = 'update services set online=0 where online=1 and mac="%s"' % (mac)
        c.execute(s1)
    db.commit()
    db.close()


def get_targets_ip(online = False):
    ''' 返回 targets 的 ip 地址列表 '''
    db = sqlite3.connect(DB_FNAME)
    c = db.cursor()
    if online:
        s0 = 'select ip from hosts'
    else:
        s0 = 'select ip from hosts where %d-last_stamp > 10' % (time.time())
    result = c.execute(s0)

    ips = [r[0] for r in result]

    db.close()
    return ips


def update_target_descr(t):
    ''' t 为解析后的组播信息
        
            {
                "mac": xxx,
                "ip": xxx,
                "hosttype": xxx,

                "services": [
                    { 'type': 'ptz', 'id': 'teacher', 'private': 'xx' },
                    { 'type': 'ptz', 'id': 'student', 'private': 'xx' },
                    { 'type': 'recording', 'id': 'recording', 'private': 'xx' },
                    ....
                ]
            }
    '''
    db = sqlite3.connect(DB_FNAME)
    c = db.cursor()

    try:

        s0 = 'delete from hosts where mac="%s"' % (t['mac'])
        c.execute(s0)
    
        s1 = 'insert into hosts values ("%s", "%s", "%s", %d)' % (t['mac'], t['ip'], t['hosttype'], time.time())
        c.execute(s1)
    
        s2 = 'delete from services where mac="%s"' % (t['mac']) # 删除所有对应的服务
        c.execute(s2)
    
        for s in t['services']:
            s3 = 'insert into services values ("%s", "%s", "%s", "%s", %d, "%s")' %\
                    (t['mac'], t['ip'], s['type'], s['id'], 0, s['private'])
            
            c.execute(s3)
                 
        db.commit()
        db.close()

    except Exception as e:
        print e


__db_init()


if __name__ == '__main__':
    __db_init()


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

