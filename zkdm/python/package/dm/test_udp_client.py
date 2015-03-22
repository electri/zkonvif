# coding: utf-8 # @file: test_udp_client.py
# @date: 2014-12-29
# @brief:
# @detail:
#
#################################################################
import socket
import sys

HOST, PORT = "localhost", 9999
data = " ".join(sys.argv[1:])
print data
#SOCK_DGRAM is the socket type to use for UDP sockets
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print 'sock' , sock
sock.sendto(data + "\n", (HOST, PORT))
print 'already sendto'
received = sock.recv(1024)
print 'already recv'

print "Sent: {}",format(data)
print "Received:{}".format(received)




# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

