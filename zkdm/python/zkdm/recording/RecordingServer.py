# coding: utf-8

from tornado.web import *
from tornado.ioloop import IOLoop
from tornado.gen import  *
import urllib, urllib2
import thread, time, sys, io
import socket
import json

from RecordingCommand import RecordingCommand
from ClassSchedule import Schedule
from DiskManagement import del_dir_schedule
from tornado.options import define, options
from CardServer import start_card_server
from LivingServer import StartLiving
sys.path.append('../')
from common.utils import zkutils
from common.reght import RegHt
from common.uty_token import *


# 必须设置工作目录 ...
os.chdir(os.path.dirname(os.path.abspath(__file__)))
_service = {"complete":False,"ids":[]}

def _param(req, key):
    if key in req.request.arguments:
        return req.request.arguments
    else:
        return None

_rcmd = None
_class_schedule = None
rh = None
_tokens = load_tokens('../common/tokens.json')


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Use the /recording/help for more help !")

class HelpHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('help.html')

class CmdHandler(tornado.web.RequestHandler):
    def get(self,token,service_id):
        rc={}
        rc['result']='ok'
        rc['info']=''
        ip = ''
        hosttype = None


        global _tokens

        if token == '0':
            ip = '127.0.0.1'
            hosttype = "x86" # ??
        else:
            if token not in _tokens:
                rc['result'] = 'error'
                rc['info'] = 'the %sth host does not exit'%token
                self.write(rc)
                return
            else:
                hosttype = _tokens[token]['hosttype']
                id_port = get_private_from_tokens(token,service_id,'recording',_tokens)
                ip = id_port['ip']


        cmd = self.get_argument('RecordCmd','nothing')

        if cmd == 'RtspPreview':
            rc = _rcmd.preview(ip,hosttype)
            self.write(rc)
            return
        elif cmd == 'UpdateClassSchedule':
            rc = _class_schedule.analyse_json(ip,hosttype)
            self.write(rc)
            return 
        elif cmd == 'RTMPLiving':
            rc = StartLiving(ip,hosttype)
            self.write(rc)
            return
        else:
            args = (self.request.uri.split('?'))[1]
            print args
            rc=_rcmd.send_command(args,ip)
            self.set_header('Content-Type', 'application/json')
            self.write(rc)

        return

_ioloop = None # 用于支持外面的结束 ...

class InternalHandler(RequestHandler):
    def get(self):
        rc = {}
        rc['result'] = 'ok'
        rc['info'] = ''

        command = self.get_argument('command', 'nothing')
        if command == 'exit':
            global rh
            rh.join()
            self.set_header('Content-Type', 'application/json')
            rc['info'] = 'exit!!!!'
            self.write(rc)
            _ioloop.stop()
        elif command == 'version':
            self.set_header('Content-Type', 'application/json')
            rc['info'] = 'now version not supported!'
            rc['result'] = 'err'
            self.write(rc)
        elif command =='services':
            self.set_header('Content-Type', 'application/json')
            self.write(_service)

_ioloop = IOLoop.instance()
def main():
    try:
        tornado.options.parse_command_line()
        application = tornado.web.Application([
            url(r"/", MainHandler),
            url(r"/recording/([^\/]+)/([^\/]+)/cmd",CmdHandler), #这里的 url 格式，必须与 tokens.json 中对应起来
            url(r"/recording/help", HelpHandler),
            url(r"/recording/internal",InternalHandler),
        ])
        application.listen(10006)

        global _rcmd
        _rcmd = RecordingCommand()

        start_card_server()

        stype = 'recording'
        reglist = gather_sds('recording', '../common/tokens.json')

        #处理本机
        service_url = r'http://<ip>:10006/recording/0/recording'
        local_service_desc = {'type':stype, 'id':'recording', 'url':service_url}
        reglist.append(local_service_desc)
        _rcmd.send_command('RecordCmd=SetFileProperty&FileFormat=mp4&TotalFilePath=C:/RecordFile')
        global _class_schedule
        _class_schedule = Schedule(None)
        _class_schedule.analyse_json('127.0.0.1','x86')
        _class_Schedule.restart_rtmp_living()
        del_dir_schedule()

        global rh
        rh = RegHt(reglist)

        global _ioloop
        _ioloop.start()

    except Exception as error:
        print error
       
def is_running(ip,port):
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
       
if __name__ == "__main__":
    result = is_running('127.0.0.1',10006)
    if result == False:
        main()

