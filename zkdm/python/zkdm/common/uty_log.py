#!/usr/bin/python
# coding: utf-8
#
# @file: uty_log.py
# @date: 2015-03-12
# @brief:
# @detail: 将日志写入 ../log/logs.db
#
#################################################################

import sqlite3 as sql
import time, os

abspath = os.path.dirname(os.path.abspath(__file__))
DBNAME = abspath + '/../log/logs.db'
print DBNAME


FAULT = 0
ERROR = 1
WARNING = 2
INFO = 3
DEBUG = 4

def log(info, project = 'unknown', level = DEBUG):
    ''' 保存日志，必须保证 DBNAME 有效 '''
    if len(info) > 1000:
        info = info[:1000]
    info = info.replace('"', "'")

    if level > DEBUG:
        level = DEBUG

    try:
        s1 = 'insert into log (project, level, stamp, content) values("%s",%d,%d,"%s")' % (project, \
                level, time.time(), info)
    except Exception as e:
        print 'Exception: log:', e
        return

    try:
        conn = sql.connect(DBNAME)
        c = conn.cursor()
        c.execute(s1)
        conn.commit()
        conn.close()
    except Exception as e:
        print 'Exception: log:', e

    

if __name__ == "__main__":
    log('test1 info')
    log('test2 "info"')
    log('test3', project='Test', level=99)


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

