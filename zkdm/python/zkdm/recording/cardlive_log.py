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
    filename = r'C:\Program Files\Zonekey\WindowsRecordServiceSetup\RecordService\CardLive\rtmp_url.log'
    rc = {}
    rc['result'] = 'ok'
    rc['info'] = ''
    content = ''
    info = {}
    s = ''
    if os.path.exists(filename):
        f = open(filename)
        line = f.readline()
        while line:
            content = content + line.strip('\n')
            s = s + line
            line = f.readline()
        str_list = content.split(';')
        for s in str_list:
            if 'start' in s.lower():
                s_list = s.split(':')
                info['start'] = s_list[1]
            elif 'stop' in s.lower():
                s_list = s.split(':')
                info['stop'] = s_list[1]
            if 'teacher' in s.lower():
                info['card0'] = s
            if 'teacher_full' in s.lower():
                info['card1'] = s
            if 'student' in s.lower():
                info['card2'] = s
            if 'student_full' in s.lower():
                info['card3'] = s
            if 'vga' in s.lower():
                info['card4'] = s
            if 'blackboard_writing' in s.lower():
                info['card5'] = s
            if 'movie' in s.lower():
                info['card6'] = s
        rc['info'] = info
        return rc
    else:
        rc['result'] = 'error'
        rc['info'] = 'file not exit!'
        return rc

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
