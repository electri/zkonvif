#!/usr/bin/python
# coding: utf-8
#
# @file: test_udp.py
# @date: 2015-03-11
# @brief:
# @detail:
#
#################################################################

import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto("ping",("172.16.1.148", 2099))
sock.sendto("ping", ("192.168.12.1", 2055))
pong, remote = sock.recvfrom(10)



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

