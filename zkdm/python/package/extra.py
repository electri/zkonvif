#!/usr/bin/python
# coding: utf-8
# 
# @file: extra.py
# @date: 2015-03-19
# @brief:
# @detail:
#
#################################################################

import os, sys, shutil

def install():
    ''' 在这里执行任意安装操作，如杀掉某某进程，替换文件，或者卸载
        软件包，安装软件包 ...
    '''

    # 使用 taskkill 杀掉 cardlive.exe 进程
    # 然后强制复制文件 ...
    print 'to replace cardlive.exe'
    try:
        os.system('taskkill /im /f cardlive.exe')
        shutil.copyfile('patch/cardlive.exe', 'c:/program files/zonekey/cardlive/cardlive.exe')
    except Exception as e:
        print 'Excp: replace cardlive.exe:', e

    # 停止录播进程，卸载录播软件，安装新的版本 ..






# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

