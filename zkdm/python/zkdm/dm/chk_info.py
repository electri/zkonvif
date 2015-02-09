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

PNAME = 'cardlive.exe' # 

def wait_cardlive():
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
	    else:
	        print 'INFO: %s is running, thread count: %d' % (PNAME, f[1])
	
	    time.sleep(10.0)

        if f and f[1] > 35:
            print 'OK: cardlive.exe has %d threads' % f[1]
            break




# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

