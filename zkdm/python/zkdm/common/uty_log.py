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


def log(info, project = 'unknown', level = 9):
    ''' 保存日志，必须保证 DBNAME 有效 '''
    info = info.replace('"', "'")

    s1 = 'insert into log (project, level, stamp, content) values("%s",%d,%d,"%s")' % (project, 
            level, time.time(), info)

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

