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
        baseOp(insert_str)

    def emptyTable(self, table_name):
        empty_str = 'DELETE FROM %s'%(table_name)
        baseOp(empty_str)
    
    def selectByOpt(self, table_name, opt):
        select_str = 'SELECT * FROM %s WHERE %s'%(table_name, opt)
        #FIXME:注意,返回值是[]或(),需要确认 ...
        return baseOp(select_str, True)

    def selectAll(self, table_name):
        select_str = 'SELECT * FROM %s'%(table_name)
        return baseOp(select_str)
        
    def alterValue(self, table_name, value):
        insert_str = 'REPLACE INTO %s VALUE %s'%(table_name, value)
        return baseOp(insert_str)

    def baseOp(self, cmd, query = False): 
        c = self.conn.cursor()
        c.execut(cmd)
        if not query:
            self.conn.commit()


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

