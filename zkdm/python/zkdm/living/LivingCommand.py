# coding: utf-8

import socket
import codecs
import getopt, sys

class LivingCommand():
    """
    """
    def __init__(self):
        pass	


    #录像程序的命令接收端口号固定为1230
    def send_command(self,command):
        rc={}
        rc['result']='ok'
        rc['info']=''
        try:
            s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            host='172.16.1.14'
            port=1230
            s.connect((host,port))
            s.send(command+"\n")
            s.recv(3)  #去除UTF-8 BOM
	    message=s.recv(512)
	    rc['info']=message
	    print message
	    s.close()

	    return rc
        except Exception as err:
            rc['result']='error'
            rc['info']=str(err)

            return rc

    def start(self):
        rc=self.send_command('BroadCastCmd=StartBroadCast')
        return rc

    def stop(self):
        rc=self.send_command('BroadCastCmd=StopBroadCast')
        return rc

    def property(self,args):
        rc=self.send_command(args)
        return rc


def main():
    ss=LivingCommand()
    ss.start()


if __name__ == "__main__":
    main()
