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
            print command
            command = command.encode('utf-8')
            print command
            s.send(command+"\n")
            s.recv(3)  #去除UTF-8 BOM
	    message=s.recv(512)
	    rc['info']=message
	    s.close()
	    return rc
        except Exception as err:
            rc['result']='error'
            rc['info']=str(err)
            return rc

    def preview(self):
        rc={}
        rc['result']='ok'
        ip = self.send_command('BroadCastCmd=GetDeviceIP')
        if(ip['result'] == 'ok' and len(ip['info'])>0):            
            ip = ip['info']
            ip = ip[:-2]
            url = {}
            url['resource1'] = 'rtsp://root:root@'+ ip +':554/session0.mpg'
            url['resource2'] = 'rtsp://root:root@'+ ip +':554/session1.mpg'
            url['resource3'] = 'rtsp://root:root@'+ ip +':554/session2.mpg'
            url['resource4'] = 'rtsp://root:root@'+ ip +':554/session3.mpg'
            url['resource5'] = 'rtsp://root:root@'+ ip +':554/session4.mpg'
            url['resource6'] = 'rtsp://root:root@'+ ip +':554/session5.mpg'
            url['movie'] = 'rtsp://root:root@'+ ip +':554/session6.mpg'
            rc['info'] = url
        else:
            rc['result'] = 'error'
            rc['info'] = ip['info']
        
        return rc


def main():
    ss=RecordingCommand()
    ss.start()

if __name__ == "__main__":
    main()
