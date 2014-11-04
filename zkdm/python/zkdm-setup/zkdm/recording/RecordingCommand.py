# coding: utf-8

import socket
import getopt, sys

class RecordingCommand():
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
            host='127.0.0.1'
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
        rc=self.send_command('RecordCmd=StartRecord')
        return rc

    def pause(self):
        rc=self.send_command('RecordCmd=PauseRecord')
        return  rc

    def stop(self):
        rc=self.send_command('RecordCmd=StopRecord')
        return rc
	
    def resume(self):
        rc=self.send_command('RecordCmd=ResumeRecord')
        return rc

    def other_command(self,args):
        rc=self.send_command(args)
        return rc

def main():
    ss=RecordingCommand()
    ss.start()

if __name__ == "__main__":
    main()
