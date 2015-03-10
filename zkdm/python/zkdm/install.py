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
sys.path.append('autoupdate')
import autoupdate.uty_au as uty

def setup():
	''' 替换 dm/DMWinService.py '''

	old = 'c:/zkdm/dm/DMWinService.py'

    mac, ip = uty.get_mac_ip()
    print 'my mac:', mac
    print 'my ip:', ip

	try:
		print 'rm old'
		os.remove(old)
	except:
		pass

	try:
		print 'replace ...'
		shutil.move('dm/DMWinService.py', old)
	except:
		pass




# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

