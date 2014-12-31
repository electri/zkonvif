# coding: utf-8
# @file: DbOp.py
# @date: 2014-12-29
# @brief:
# @detail:
#
#################################################################
import sqlite3, sys, time
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
        
    def alterTableValue(value):
        db = DbOp.DbOp('Proxied_hosts.db')
        db = dbop.dbop('proxied_hosts')
        db.altervalue('hosts_state', (str(value[0]), value[1]))
        db.close()

    def LoadTable(fname):
        hds =  uty_token.gather_hds(fname);
        hips = []
        for hd in hds:
            hips.append(hd['ip'])
            
        db = DbOp.DbOp('proxied_hosts.db')
        db.emptyTable('hosts_state')
        temps = {}
        for hip in hips:
            print hip
            temps.update({str(hip):{'isLive':0, 'timesstamp':None}})
        print temps    
        for hip in hips:
        #FIXME:崩溃,往表里面不能插入 unicode
            db.insertTable('hosts_state', (str(hip), 0))

        db.close()
        return temps



def _db_init():
    ''' 检查数据库, 如果 hosts_state 表不存在，则创建之
    '''
    db = sqlite3.connect(DB_FNAME)
    c = db.cursor()
    s0 = 'select COUNT(*) from sqlite_master where name="hosts_state"'
    rc = c.execute(s0)
    if int(rc.next()[0]) == 0:
        s1 = 'create table hosts_state(ip varchar(128), isLive integer, last_stamp integer)'
        c.execute(s1)
    db.commit()
    db.close()


def db_init_from_tokens(fname):
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

    t = time.time()
    for ip in ips:
        s1 = 'insert into hosts_state values("%s", 0, %d)' % (ip, t)
        c.execute(s1)

    db.commit()
    db.close()


def db_check_timeout(curr_time, timeout = 10):
    ''' 修改超时的记录，默认 10 秒超时 

        WARNING: 必须保证 _db_init() 有效
    '''
    s0 = 'update hosts_state set isLive=0 where last_stamp < %d' % (curr_time - timeout)
    db = sqlite3.connect(DB_FNAME)
    c = db.cursor()
    c.execute(s0)
    db.commit()
    db.close()


def db_update(remote_ip):
    ''' 更新 remote_ip 对应的记录，isLive 修改为 1，last_stamp 修改为当前时间 

        WARNING: 必须保证 _db_init() 有效
                 如果 remote_ip 不在 hosts_state，不必关心，因为非被代理主机不会发送 pong 的
    '''
    s0 = 'update hosts_state set isLive=1, last_stamp=%d where ip="%s"' % (time.time(), remote_ip)
    db = sqlite3.connect(DB_FNAME)
    c = db.cursor()
    c.execute(s0)
    db.commit()
    db.close()

    

if __name__ == '__main__':
    db_init_from_tokens('../common/tokens.json')
    db_update("192.168.12.33")
    time.sleep(15)
    db_check_timeout(time.time())
    sys.exit()

    db = DbOp('proxied_hosts.db')
    db.alterValue('hosts_state', ('172.16.1.10', 1))
    t = db.selectByOpt('hosts_state', "isLive = '1'") 
    print type(t)    
    for e in t:
        print e    
    db.close()
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

