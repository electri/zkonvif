# coding: utf-8
# @file: query.py
# @date: 2014-12-22
# @brief:
# @detail: 实现各种查询，哦，这个文件是最需要扩展的，满足各种查询条件
#
#################################################################


from dbhlp import DBHlp


def getAllServices(offline = False):
    ''' 返回服务列表 '''
    return { 'result': 'ok', 'info': '', 'value':[] }


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

