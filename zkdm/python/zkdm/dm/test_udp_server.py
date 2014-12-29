# coding: utf-8
# @file: test_udp_server.py
# @date: 2014-12-29
# @brief:
# @detail:
#
#################################################################
import SocketServer

class MyUDPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        print 'socket', socket
        print "{} wrote:".format(self.client_address[0])
        socket.sendto(data.upper(), self.client_address)

if __name__ == "__main__":
    HOST, PORT = "localhost", 9999
    server = SocketServer.UDPServer((HOST, PORT), MyUDPHandler)
    print 'server socket', server
    server.serve_forever()
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

