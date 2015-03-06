#!/usr/bin/python
# coding: utf-8
#
# @file: ns_query.py
# @date: 2015-01-13
# @brief:
# @detail: 具体服务应 import 此模块，
#
#################################################################



import sqlite3, os

fpath = os.path.abspath(__file__)
DB_FNAME = os.path.dirname(fpath) + "/../ns/ns.db"


def get_hosttype(tid):
    ''' 根据 token id 查询对应的主机类型，如果找不到 token id，则返回 None '''
    db = sqlite3.connect(DB_FNAME)
    c = db.cursor()

    s0 = 'select type from hosts where mac="%s"' % (tid)
    result = c.execute(s0)

    x = [r[0] for r in result]

    db.close()

    if len(x) == 0:
        return None
    else:
        return x[0] # 返回 hosttype


def get_private(tid, stype, sid):
    ''' 返回特定服务的 private 信息, 如果查不到，返回 None，

        tid: token id
        stype: service type
        sid: service id

        返回 private, online
    '''
    db = sqlite3.connect(DB_FNAME)
    c = db.cursor()

    s0 = 'select private,online from services where mac="%s" and type="%s" and id="%s"' % (tid, stype, sid)
    result = c.execute(s0)
    
    x = [(r[0], r[1]) for r in result]

    db.close()

    if len(x) == 0:
        return None
    return x[0][0], x[0][1]





# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

