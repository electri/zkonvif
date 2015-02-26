#!/usr/bin/python
# coding: utf-8
#
# @file: CommonHelper.py
# @date: 2015-02-04
# @brief:
# @detail:
#
#################################################################
import socket

def is_running(ip='127.0.0.1',port=10006):
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)  
    try:  
        s.connect((ip,int(port)))
        s.shutdown(2)
        #利用shutdown()函数使socket双向数据传输变为单向数据传输。shutdown()需要一个单独的参数，  
        #该参数表示了如何关闭socket。具体为：0表示禁止将来读；1表示禁止将来写；2表示禁止将来读和写。  
        s.close()
        return True  
    except Exception as error:
        return False 


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
