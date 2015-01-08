#!/usr/bin/python
# coding: utf-8
#
# @file: dbhlp.py
# @date: 2015-01-08
# @brief:
# @detail:
#
#################################################################

import sqlite3, time


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
                info varchar(4096), last_stamp integer)'
        c.execute(s1)

    if not __tab_is_exist(c, "services"):
        s1 = 'create table services(mac varchar(64), ip varchar(64), type varchar(16),\
                id varchar(16), url varchar(256), online integer, private varchar(1024))'
        c.execute(s1)

    db.commit()
    db.close()


def update_target_pong(stamp, ip):
    ''' 更新 hosts 中，ip 对应的主机的 last_stamp '''
    db = sqlite3.connect(DB_FNAME)
    c = db.cursor()
    s1 = 'update hosts set last_stamp=%d where ip="%s"' % (stamp, ip)
    c.execute(s1)
    db.commit()
    db.close()


def chk_timeout(curr):
    ''' 更新所有 curr - hosts.last_stamp > 10 的主机的所有服务的 online 为 0 '''
    db = sqlite3.connect(DB_FNAME)
    c = db.cursor()
    s0 = 'select mac from hosts where %d-last_stamp > 10' % (curr)
    result = c.execute(s0)
    for r in result:
        mac = r[0]
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


__db_init()


if __name__ == '__main__':
    __db_init()


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

