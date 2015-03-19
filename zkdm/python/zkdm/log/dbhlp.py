# coding: utf-8

import sqlite3
import time


DBNAME = 'logs.db'
TABLENAME = 'log'
KEEP_DAYS = 3 # 保留三天的历史

S0 = r'create table log (id integer primary key, project varchar(64), level integer, stamp integer, content text)' 

class DBHlp:
    ''' 封装到 sqlite3 的读写 '''
    def __init__(self):
        self.__conn = None
        pass


    def __db_open(self):
        self.__conn = sqlite3.connect(DBNAME)
        return self.__conn.cursor()


    def __db_close(self):
        self.__conn.commit()
        self.__conn.close()
        self.__conn = None


    def save(self, project, level, stamp, content):
        c = self.__db_open()
        s0 = r'insert into log (project, level, stamp, content) values ("{}",{},{},"{}")'.format(project, level, stamp, content)
        c.execute(s0)
        self.__db_close()


    def query(self, project = None, level = None, stamp_begin = None, stamp_end = None):
        ''' 查询：总是返回数组
            [
                 { item ...}, { item ... } ...
             ]
        '''
        if not stamp_begin:
            stamp_begin = 0
        if not stamp_end:
            stamp_end = time.time()

        rc = []
        c = self.__db_open()
        s0 = r'select * from log where stamp > {} and stamp < {}'.format(stamp_begin, stamp_end)
        if project is not None:
            s0 += r' and project="{}"'.format(project)
        if level is not None:
            s0 += r' and level <= {}'.format(level)

        print s0

        for item in c.execute(s0):
            it = {}
            it['project'] = item[1]
            it['level'] = item[2]
            it['stamp'] = item[3]
            it['content'] = item[4]
            rc.append(it)
        
        self.__db_close()
        return rc
        


def __check_init():
    ''' 检查数据库是否准备好 '''
    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()
    # 检查 log 表是否存在 ...
    s1 = 'select COUNT(*) from sqlite_master where name="' + TABLENAME + '"'
    v = c.execute(s1)

    exist = (c.execute(s1).next()[0] != 0)
    if not exist:
        print 'to init db ...'
        c.execute(S0)
    else:
        # 删除 N 天之前的历史
        print TABLENAME, 'existed! to remove tooooo old data'
        stamp_last = time.time() - KEEP_DAYS * 24 * 3600
        s2 = 'delete from log where stamp < %d' % stamp_last
        c.execute(s2)
    conn.close()


# 保证数据结构 ...
__check_init()


if __name__ == '__main__':
    print 'testing'

    db = DBHlp()
    db.save('test me', 99, time.time(), r"{'key':22, 'code':-102, 'descr':'cant open file'}")
    r = db.query()
    print r
