#!/usr/bin/python
# coding: utf-8
#
# @file: Check_CardLive.py
# @date: 2015-02-05
# @brief:
# @detail:
#
#################################################################

import wmi, pythoncom

PNAME = 'CardLive.exe'

def CardLive_Runing():
    pythoncom.CoInitialize()
    w = wmi.WMI()
    cs = [(ps.Name, ps.ThreadCount) for ps in w.Win32_Process()]
    f = None
    
    for c in cs:
        if c[0].lower() == PNAME.lower():
            f = c
            break

    if f is None:
        return False
    else:
        if f[1]>34:
            return True
        else:
            return False
