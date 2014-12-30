# coding: utf-8
# @file: DbOp.py
# @date: 2014-12-29
# @brief:
# @detail:
#
#################################################################
import sqlite3


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

if __name__ == '__main__':
    db = DbOp('proxied_hosts.db')
    db.alterValue('hosts_state', ('172.16.1.10', 1))
    t = db.selectByOpt('hosts_state', "isLive = '1'") 
    print type(t)    
    for e in t:
        print e    
    db.close()
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

