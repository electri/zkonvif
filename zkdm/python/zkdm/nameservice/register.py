# coding: utf-8
# @file: register.py
# @date: 2014-12-22
# @brief:
# @detail: 处理 reghost, regservice, heartbeat ... 
#
#################################################################


from dbhlp import DBHlp

def reghost(params):
    ''' 注册主机信息，写入数据库 
        params 中，至少包含 
            name: 唯一名字，可以使用 mac ?
            type: 主机类型
    '''
    print 'reghost: ', params
    return { 'result': 'ok', 'info': 'success' }


def regservice(params):
    ''' 注册服务信息，写入数据库
        host_name, service_name, service_type, service_url
    '''
    print 'regservice: ', params
    return { 'result': 'ok', 'info': 'success' }


def heartbeat(params):
    ''' 心跳，更新服务状态列表
        host_name, service_name, service_type
    '''
    print 'heartbeat: ', params
    return { 'result': 'ok', 'info': 'success' }


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

