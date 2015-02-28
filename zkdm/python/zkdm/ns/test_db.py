#!/usr/bin/python
# coding: utf-8
#
# @file: test_db.py
# @date: 2015-01-13
# @brief:
# @detail:
#
#################################################################

import dbext as db

MAC = 'AABB112233CC'
STYPE = 'ptz'
SID = 'teacher'

hosttype = db.get_hosttype(MAC)
print hosttype

private = db.get_private(MAC, STYPE, SID)
print private




# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

