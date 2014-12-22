# coding: utf-8
# @file: query.py
# @date: 2014-12-22
# @brief:
# @detail: 实现各种查询，哦，这个文件是最需要扩展的，满足各种查询条件
#
#################################################################


from dbhlp import DBHlp


def getAllServices(params):
    ''' 返回服务列表 '''
    offline = False
    if 'offline' in params and params['offline'] == '1':
        offline = True

    s = 'select * from services'
    if not offline:
        s = 'select services.host, services.name, services.type, services.url from services join \
            states on (services.host=states.host and services.name=states.name and \
                    services.type=states.type)'
    db = DBHlp()
    c = db.db_open()
    rc = db.query(c, s)

    value = []
    for rec in rc:
        item = {}
        item['host'] = rec[0]
        item['name'] = rec[1]
        item['type'] = rec[2]
        item['url'] = rec[3]
        value.append(item)

    db.db_close()
    return { 'result': 'ok', 'info': '', 'value':value }


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

