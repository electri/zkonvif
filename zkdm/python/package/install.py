#!/usr/bin/python
# coding: utf-8
#
# @file: install.py
# @date: 2015-03-09
# @brief:
# @detail:
#
#################################################################

import os, shutil, sys
import uty_au as uty

def setup():
    mac, ip = uty.get_mac_ip()
    print 'my mac:', mac
    print 'my ip:', ip

    # 测试


    ''' 本次更新主要是启用日志服务，
        日志服务本身不进行服务注册和心跳，
        其他服务通过 ../common/uty_log.py 保存日志

    '''
    # 更像日志服务
    for f in os.listdir('log/'):
        if f == 'logs.db' and os.path.isfile('c:/zkdm/log/logs.db'):
            continue
        pf = 'log/' + f
        if os.path.isfile(pf):
            shutil.copyfile(pf, 'c:/zkdm/log/' + f)

    # 更新 recording 服务, 简单的复制目录中所有文件
    for f in os.listdir('recording/'):
        pf = 'recording/' + f
        if os.path.isfile(pf):
            shutil.copyfile(pf, 'c:/zkdm/recording/' + f)

    # 更新 dm 服务，简单的复制目录中所有文件
    for f in os.listdir('dm/'):
        pf = 'dm/' + f
        if os.path.isfile(pf):
            shutil.copyfile(pf, 'c:/zkdm/dm/' + f)

    # 更新 ptz 服务，简单的复制目录中所有文件
    for f in os.listdir('ptz/'):
        pf = 'ptz/' + f
        if os.path.isfile(pf):
            shutil.copyfile(pf, 'c:/zkdm/ptz/' + f)

    

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

