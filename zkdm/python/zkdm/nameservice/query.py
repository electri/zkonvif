# coding: utf-8
# @file: query.py
# @date: 2014-12-22
# @brief:
# @detail: 实现各种查询，哦，这个文件是最需要扩展的，满足各种查询条件
#
#################################################################


from dbhlp import DBHlp

def getHosts(params):
    ''' 返回匹配的注册的主机,  host, type 为可选 
    '''
    s = 'select * from hosts'
    if 'host' in params and 'type' in params:
        s = 'select * from hosts where host="%s" and type="%s"' % (params['host'], params['type'])
    elif 'host' in params:
        s = 'select * from hosts where host="%s"' % (params['host'])
    elif 'type' in params:
        s = 'select * from hosts where type="%s"' % (params['type'])
    
    db = DBHlp()
    rc = db.query(s)
    value = []
    for rec in rc:
        item = {}
        item['host'] = rec[0]
        item['type'] = rec[1]
        value.append(item)
    return { 'result': 'ok', 'info':'', 'value':value }


def getAllServices(params):
    ''' 返回服务列表, offline 可选 '''
    offline = False
    if 'offline' in params and params['offline'] == '1':
        offline = True

    s = 'select * from services'
    if not offline:
        s = 'select services.host, services.name, services.type, services.url from services join \
            states on (services.host=states.host and services.name=states.name and \
                    services.type=states.type)'
    db = DBHlp()
    rc = db.query(s)

    value = []
    for rec in rc:
        item = {}
        item['host'] = rec[0]
        item['name'] = rec[1]
        item['type'] = rec[2]
        item['url'] = rec[3]
        value.append(item)

    return { 'result': 'ok', 'info': '', 'value':value }


def getServicesByType(params):
    ''' 返回 type 指定的服务列表，offline, host 可选
    '''
    offline = False
    if 'offline' in params and params['offline'] == '1':
        offline = True

    t = ''
    if 'type' not in params:
        return { 'result': 'err', 'info': 'type MUST be supplied' }
    else:
        t = params['type']

    s = 'select * from services where type="%s"' % (t)

    # 四种可能： offline X host
    if 'host' in params:
        host = params['host']
        if not offline:
            s = 'select services.host, services.name, services.type, services.url from services join \
                states on (services.host=states.host and services.name=states.name and \
                        services.type=states.type) where (services.host="%s" and services.type="%s")' % (host, t)
        else:
            s = 'select * from services where host="%s" and type="%s"' % (host, t)
    elif not offline:
        s = 'select services.host, services.name, services.type, services.url from services join \
            states on (services.host=states.host and services.name=states.name and \
                    services.type=states.type) where services.type="%s"' % (t)

    db = DBHlp()
    rc = db.query(s)
    value = []
    for rec in rc:
        item = {}
        item['host'] = rec[0]
        item['name'] = rec[1]
        item['type'] = rec[2]
        item['url'] = rec[3]
        value.append(item)
    return { 'result': 'ok', 'info':'', 'value':value }


def getServicesByHost(params):
    ''' 返回指定 host 的所有服务，offline 可选 '''
    offline = False
    if 'offline' in params and params['offline'] == '1':
        offline = True

    if 'host' not in params:
        return { 'result': 'err', 'info': 'host MUST be supplied' }
        
    s = 'select * from services where host="%s"' % (params['host'])
    if not offline:
        s = 'select services.host, servics.name, services.type, services.url from services join \
            states on (services.host=states.host and services.name=states.name and services.type=states.type) \
            where services.host="%s"' % (params['host'])
    db = DBHlp()
    rc = db.query(s)
    value = []
    for rec in rc:
        item = {}
        item['host'] = rec[0]
        item['name'] = rec[1]
        item['type'] = rec[2]
        item['url'] = rec[3]
        value.append(item)
    return { 'result': 'ok', 'info':'', 'value': value }

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

