#!/usr/bin/python
# coding: utf-8

# @file: test_sqlite3.py
# @date: 2014-12-26
# @brief:
# @detail: 测试多线程访问同一个 sqlite3 对象
#
#################################################################

import threading, sqlite3, time, os

DB_FNAME = 'test.db'

def prepare():
    ''' 准备测试用的数据库，表 test，插入 1000 条记录 '''
    conn = sqlite3.connect(DB_FNAME)
    cursor = conn.cursor();
    
    s0 = 'select COUNT(*) from sqlite_master where name="%s"' % ('test')
    rc = cursor.execute(s0)
    x = rc.next()
    if x[0] == 0:
        s1 = 'create table test (info varchar(64), stamp integer)'
        cursor.execute(s1)
        
        for i in range(0, 1000):
            s2 = 'insert into test values("origin", %d)' % i
            cursor.execute(s2)
        conn.commit()
    conn.close()


class Writer(threading.Thread):
    ''' 写测试线程，每次更新所有记录的 info，'''
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.__quit = False
        self.__cnt = 0
        self.test_cnt = 0
        self.start()

    def join(self):
        self.__quit = True
        threading.Thread.join(self)

    def run(self):
        while not self.__quit:
            self.__run_once()
            time.sleep(0.1)

    def __run_once(self):
        conn = sqlite3.connect(DB_FNAME)
        c = conn.cursor()

        s0 = 'select COUNT(*) from test'
        rc = c.execute(s0)
        cnt = int(rc.next()[0])
        for i in range(0, cnt):
            s1 = 'select info from test where stamp=%d' % i
            rc = c.execute(s1)
            s = ''
            for x in rc: 
                s = x[0]
                break;
            
            self.__cnt += 1

            s2 = 'update test set info="%s" where stamp=%d' % (self.__cnt, i)
            self.test_cnt += 1
            c.execute(s2)
        conn.commit()
        conn.close()


class Reader(threading.Thread):
    ''' 读线程，循环 select '''
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.test_cnt = 0
        self.start()

    def run(self):
        while True:
            self.__run_once()
            time.sleep(0.01)

    def __run_once(self):
        conn = sqlite3.connect(DB_FNAME)
        c = conn.cursor()

        s0 = 'select COUNT(*) from test'
        rc = c.execute(s0)
        self.test_cnt += 1
        cnt = int(rc.next()[0])
        for i in range(0, cnt):
            s1 = 'select * from test where stamp=%d' % i
            rc = c.execute(s1)
            self.test_cnt += 1
        conn.commit()
        conn.close()


if __name__ == '__main__':
    prepare()

    w = Writer()
    r = Reader()

    time.sleep(10.0)

    print os.getpid(), 'update: %d, select: %d' % (w.test_cnt, r.test_cnt)



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

