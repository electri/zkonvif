# coding: utf-8
# @file: register.py
# @date: 2014-12-22
# @brief:
# @detail: 处理 reghost, regservice, heartbeat ... 
#
#################################################################

from dbhlp import *
import time

def is_host_exist(db, name):
    ''' select COUNT(*) from tab where name=key '''
    s = 'select COUNT(*) from %s where name="%s"' % (TAB_HOSTS, name)
    rc = db.query(s)
    if len(rc) > 0 and int(rc[0][0]) != 0:
        return True
    else:
        return False

def is_service_exist(db, host, name, t):
    s = 'select COUNT(*) from %s where host="%s" and name="%s" and type="%s"' % \
        (TAB_SERVICES, host, name, t)
    rc = db.query(s)
    if len(rc) > 0 and int(rc[0][0]) != 0:
        return True
    else:
        return False

def update_states(db, host, name, t, stamp):
    ''' 更新心跳 '''
    s = 'select COUNT(*) from %s where host="%s" and name="%s" and type="%s"' % \
        (TAB_STATES, host, name, t)
    rc = db.query(s)

    s2 = ''
    if len(rc) > 0 and int(rc[0][0]) != 0:
        s2 = 'update %s set stamp=%d where host="%s" and name="%s" and type="%s"' % \
             (TAB_STATES, stamp, host, name, t)
    else:
        s2 = 'insert into %s VALUES("%s", "%s", "%s", %d)' % \
             (TAB_STATES, host, name, t, stamp)
    db.execute(s2)

def reghost(params):
    ''' 注册主机信息，写入数据库 
        params 中，至少包含 
            name: 唯一名字，可以使用 mac ?
            type: 主机类型
    '''
    if 'name' not in params or 'type' not in params:
        return { 'result': 'err', 'info': 'reghost MUST supply name & type' }

    s = ''
    info = 'created'
    db = DBHlp()
    if is_host_exist(db, params['name']):
        s = 'update %s set type="%s" where name="%s"' % (TAB_HOSTS, params['type'], params['name'])
        info = 'update'
    else:
        s = 'insert into %s VALUES("%s", "%s")' % (TAB_HOSTS, params['name'], params['type'])
    db.execute(s)

    return { 'result': 'ok', 'info': info }


def regservice(params):
    ''' 注册服务信息，写入数据库
        host_name, service_name, service_type, service_url
    '''
    if 'host' not in params or 'name' not in params or 'type' not in params:
        return {'result': 'err', 'info': 'regservice MUST supply host, name & type, opt url' }

    s = ''
    info = 'created'
    url = ''
    if 'url' in params:
        url = params['url']

    db = DBHlp()
    if is_service_exist(db, params['host'], params['name'], params['type']):
        s = 'update %s set url="%s" where host="%s" and name="%s" and type="%s"' % \
            (TAB_SERVICES, url, params['host'], params['name'], params['type'])
        info = "updated"
    else:
        s = 'insert into %s VALUES("%s", "%s", "%s", "%s")' %\
            (TAB_SERVICES, params['host'], params['name'], params['type'], url)
    db.execute(s)
    update_states(db, params['host'], params['name'], params['type'], time.time())

    return { 'result': 'ok', 'info': info }


def unregservice(params):
    ''' 注销服务：
    '''
    if 'host' not in params or 'name' not in params or 'type' not in params:
        return { 'result': 'err', 'info': 'unregservice MUST be supplied with host, name and type' }

    db = DBHlp()
    s = 'delete from states where host="%s" and name="%s" and type="%s"' % (params['host'], params['name'], params['type'])
    db.execute(s)
    return { 'result': 'ok', 'info':'' }


def heartbeat(params):
    ''' 心跳，更新服务状态列表
        host_name, service_name, service_type
    '''
    if 'host' not in params or 'name' not in params or 'type' not in params:
        return {'result': 'err', 'info': 'regservice MUST supply host, name & type, opt url' }

    db = DBHlp()
    update_states(db, params['host'], params['name'], params['type'], time.time())

    return { 'result': 'ok', 'info': 'updated' }


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

