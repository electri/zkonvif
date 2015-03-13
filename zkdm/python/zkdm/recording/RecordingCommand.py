# coding: utf-8

import socket
import getopt, sys
sys.path.append('../')
from common.uty_log import log

class RecordingCommand():
    """
    """
    def __init__(self):
        pass
	
    def send_command(self, command, ip='127.0.0.1'):
        rc = {}
        rc['result'] = 'ok'
        rc['info'] = ''
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        log('RecordingCommand.send_command: ip=%s, cmd=%s' % (ip, command), \
                project = 'recording')
        try:
            s.settimeout(2)
            host = ip
            port = 1230
            s.connect((host, port))
            s.settimeout(None)
            s.send(command + "\n")
            print command
            # utf8 BOM
            self.__recv_t(s, 3, 1.0)
            message = self.__recv_t(s, 512, 1.0)
            message = message.strip()
            rc['info'] = message
        except Exception as err:
            rc['result'] = 'error'
            rc['info'] = str(err)

        s.close()
        if rc['result'] == 'ok':
            log('    ok', project = 'recording')
        else:
            log('RecordingCommand.send_command: err, info=%s' % rc['info'], project = 'recording', level=1)
        return rc

    def __recv_t(self, sock, n, timeout = 2.0):
        import select
        r,w,e = select.select([sock], [], [], timeout)
        if r:
            return sock.recv(n)
        else:
            raise Exception('RECV TIMEOUT')

    def preview(self, ip, hosttype):
        rc = {}
        rc['result'] = 'ok'
        rc['info'] = ''
        log('RecordingCommand.preview: ip=%s, hosttype=%s' % (ip, hosttype), \
                project = 'recording')

        if hosttype == 'x86':
            rtsp_ip = self.send_command('BroadCastCmd=GetDeviceIP', ip)
            if(rtsp_ip['result'] == 'ok' and len(rtsp_ip['info']) > 0):            
                rtsp_ip = rtsp_ip['info']
                rtsp_ip = rtsp_ip[:-2]
                url = {}
                url['resource1'] = 'rtsp://root:root@'+ rtsp_ip +':554/session0.mpg'
                url['resource2'] = 'rtsp://root:root@'+ rtsp_ip +':554/session1.mpg'
                url['resource3'] = 'rtsp://root:root@'+ rtsp_ip +':554/session2.mpg'
                url['resource4'] = 'rtsp://root:root@'+ rtsp_ip +':554/session3.mpg'
                url['resource5'] = 'rtsp://root:root@'+ rtsp_ip +':554/session4.mpg'
                url['resource6'] = 'rtsp://root:root@'+ rtsp_ip +':554/session5.mpg'
                url['movie'] = 'rtsp://root:root@'+ rtsp_ip +':554/session6.mpg'
                rc['info'] = url
            else:
                rc['result'] = 'error'
                rc['info'] = rtsp_ip['info']
        else:
            response = self.send_command('RecordCmd=QueryRtspUrls',ip)
            if response['result'] == 'ok':
                url = {}
                infos = response['info'].split('&')
                i = 1
                for info in infos:
                    url['resource' + str(i)] = info
                    i = i+1
                rc['info'] = url
            else:
                rc['result'] = 'error'
                rc['info'] = response['info']

        if rc['result'] == 'ok':
            log('RecordingCommand.preview: ok', project = 'recording')
        else:
            log('RecordingCommand.preview: err, info=%s' % rc['info'], \
                    project = 'recording', level = 1)
        
        return rc


def main():
    ss=RecordingCommand()
    ss.send_command('11')

if __name__ == "__main__":
    main()
