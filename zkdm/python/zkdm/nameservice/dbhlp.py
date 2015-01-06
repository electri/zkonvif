# coding: utf-8

import sqlite3
import time, sys, threading


DBNAME = 'ns.db'
TABLENAME = 'log'
TAB_HOSTS = 'hosts'
TAB_SERVICES = 'services'
TAB_STATES = 'states'

S0 = r'create table log (id integer primary key, project varchar(64), level integer, stamp integer, content text)' 
S1 = r'create table hosts (name varchar(128), type varchar(128))'
S2 = r'create table services (host varchar(128), name varchar(128), type varchar(128), url varchar(255))'
S3 = r'create table states (host varchar(128), name varchar(128), type varchar(128), stamp integer)'

TABS = [ { "name": TAB_HOSTS, "create": S1 },
         { "name": TAB_SERVICES, "create": S2 },
         { "name": TAB_STATES, "create": S3 }
       ]


class DBHlp:
    ''' 封装到 sqlite3 的读写 '''
    def __init__(self):
        self.__conn = None
        pass


    def db_open(self):
        self.__conn = sqlite3.connect(DBNAME)
        return self.__conn.cursor()

    def db_close(self):
        self.__conn.commit()
        self.__conn.close()
        self.__conn = None

    def execute(self, c, sent):
        ''' 直接执行 sql 语句，没有返回 '''
        c.execute(sent)

    def query(self, c, sent):
        ''' 执行查询，返回 [] '''
        rc = []
        for rec in c.execute(sent):
            rc.append(rec)
        return rc


class FlushState(threading.Thread):
    ''' 每隔30秒，删除超时的 services '''
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.start()

    def run(self):
        while True:
            time.sleep(30)
            self.__flush()

    def __flush(self):
        s = 'delete from states where stamp < %d' % (time.time() - 30)
        db = DBHlp()
        c = db.db_open()
        db.execute(c, s)
        db.db_close()


def __check_init():
    ''' 检查数据库是否准备好 '''
    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()

    for chk in TABS:
        s1 = 'select COUNT(*) from sqlite_master where name="' + chk['name'] + '"'
        n = c.execute(s1)
        found = False
        for x in n:
            if int(x[0]) == 1:
                found = True
                break

        if not found:
            print 'INFO: dbhlp: init:', chk['name']
            c.execute(chk['create'])
        else:
            print 'INFO: dbhlp: existed:', chk['name']
    conn.close

    # 启动工作线程，每隔30秒，刷新一次 states 表
    th = FlushState()


# 保证数据结构 ...
__check_init()


