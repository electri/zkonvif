#!/usr/bin/python
# coding: utf-8
#
# @file: cardlive_log.py
# @date: 2015-02-04
# @brief:
# @detail:
#
#################################################################
import os

def cardlive_log():
    filename = r'C:\Users\wangze\Desktop\11.txt'
    rc = {}
    rc['result'] = 'ok'
    rc['info'] = ''
    s = ''
    if os.path.exists(filename):
        f = open(filename)
        line = f.readline()
        while line:
            rc['info'] = rc['info'] + line
            s = s + line
            line = f.readline()
        return rc
    else:
        rc['result'] = 'error'
        rc['info'] = 'file not exit!'
        return rc

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
