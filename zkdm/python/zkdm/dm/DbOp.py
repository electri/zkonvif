# coding: utf-8
# @file: DbOp.py
# @date: 2014-12-29
# @brief:
# @detail:
#
#################################################################
import sqlite3, sys
sys.path.append('../')
from common.uty_token import *

DB_FNAME = 'proxied_hosts.db'

# XXX: 下面对 sql 语句的使用，可能有问题,
#      sql 语句中的 char/vchar 类型，必须使用 ""，如
#      insert into hosts_state values("123.123.123.123", 1)
#      所以应该使用 'insert into %s values("%s", %d)' % ('hosts_state', '123.123.123.123', 1)
#      才行吧
class DbOp:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
     
    def insertTable(self, table_name, value):
        insert_str = 'INSERT INTO %s VALUES %s'%(table_name, value)
        
        self.baseOp(insert_str)

    def emptyTable(self, table_name):
        empty_str = 'DELETE FROM %s'%(table_name)
        self.baseOp(empty_str)
    
    def selectByOpt(self, table_name, opt):
        select_str = "SELECT * FROM %s WHERE %s"%(table_name, opt)
        #FIXME:注意,返回值是[]或(),需要确认 ...
        return self.baseOp(select_str, True)

    def selectAll(self, table_name):
        select_str = 'SELECT * FROM %s'%(table_name)
        return self.baseOp(select_str, True)
        
    def alterValue(self, table_name, value):
        insert_str = 'REPLACE INTO %s VALUES %s'%(table_name, value)
        return self.baseOp(insert_str)

    def baseOp(self, cmd, query = False): 
        c = self.conn.cursor()
        c.execute(cmd)
        if not query:
            self.conn.commit()
        return c

    def close(self):
        self.conn.close()




def _db_init():
    ''' 检查数据库, 如果 hosts_state 表不存在，则创建之
    '''
    db = sqlite3.connect(DB_FNAME)
    c = db.cursor()
    s0 = 'select COUNT(*) from sqlite_master where name="hosts_state"'
    rc = c.execute(s0)
    if int(rc.next()[0]) == 0:
        s1 = 'create table hosts_state(ip varchar(128), isLive integer)'
        c.execute(s1)
    db.commit()
    db.close()


def _db_init_from_tokens(fname):
    ''' fname 为 tokens.json，从 tokens.json 中提取被代理主机信息，然后
        更新 hosts_state 表，初始 isLive 都设置为 0
    '''
    _db_init()
    hosts = gather_hds(fname)
    ips = []
    for host in hosts:
        if host['tokenid'] == "0": # 不加载本机
            continue
        if 'ip' in host:
            ips.append(host['ip'])

    db = sqlite3.connect(DB_FNAME)
    c = db.cursor()
    s0 = 'delete from hosts_state'
    c.execute(s0)

    for ip in ips:
        s1 = 'insert into hosts_state values("%s", 0)' % (ip)
        c.execute(s1)

    db.commit()
    db.close()


if __name__ == '__main__':
    _db_init_from_tokens('../common/tokens.json')
    sys.exit()

    db = DbOp('proxied_hosts.db')
    db.alterValue('hosts_state', ('172.16.1.10', 1))
    t = db.selectByOpt('hosts_state', "isLive = '1'") 
    print type(t)    
    for e in t:
        print e    
    db.close()
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

