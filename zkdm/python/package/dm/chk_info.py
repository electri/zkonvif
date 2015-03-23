#!/usr/bin/python
# coding: utf-8
#
# @file: chk_info.py
# @date: 2015-02-04
# @brief:
# @detail:
#
#################################################################

import wmi, pythoncom, time
import sys
sys.path.append('../')
from common.uty_log import log

PNAME = 'cardlive.exe' # 

def wait():
    time.sleep(3 * 60) # 此处无条件等待3分钟
    pythoncom.CoInitialize()
    w = wmi.WMI()

    while True:
        cs = [(ps.Name, ps.ThreadCount) for ps in w.Win32_Process()]
    
        f = None
    
        for c in cs:
            if c[0].lower() == PNAME.lower():
                f = c
                break
    
        if f is None:
            print 'Warning: %s NOT running ...' % PNAME
            log('%s NOT running...'%PNAME, project='dm', level=2)
        else:
            print 'INFO: %s is running, thread count: %d' % (PNAME, f[1])
            log('%s is running, thread count=%d' % (PNAME, f[1]), project='dm', level=3)
    
        if f and f[1] > 30:
            print 'OK: cardlive.exe has %d threads' % f[1]
            break

        time.sleep(10.0)




# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

