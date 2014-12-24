# coding: utf-8

from tornado.web import *
from tornado.ioloop import IOLoop
from tornado.gen import  *
import urllib, urllib2
import thread, time, sys
import socket
import json

from RecordingCommand import RecordingCommand
from ClassSchedule import Schedule
from tornado.options import define, options
from CardServer import start_card_server
from LivingServer import StartLiving
sys.path.append('../')
from common.utils import zkutils
from common.reght import RegHt
from LogWriter import log_info, log_debug


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

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Use the /recording/help for more help !")

class HelpHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('help.html')

class CmdHandler(tornado.web.RequestHandler):
    def get(self):
        rc={}
        rc['result']='ok'
        rc['info']=''

        cmd = self.get_argument('RecordCmd','nothing')

        if cmd == 'RtspPreview':
            rc = _rcmd.preview()
            self.write(rc)
            return
        elif cmd == 'UpdateClassSchedule':
            rc = _class_schedule._analyse_json()
            self.write(rc)
            return 
        elif cmd == 'RTMPLiving':
            rc = StartLiving()
            self.write(rc)
            return
        else:
            args = (self.request.uri.split('?'))[1]
            print args
            rc=_rcmd.send_command(args)
            self.set_header('Content-Type', 'application/json')
            self.write(rc)

        
        log_info('receive:'+(self.request.uri.split('?'))[1])
        log_info('result:'+rc['result']+"\0\0\0info:"+rc['info'])

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
            log_info('exit service！')
            _ioloop.stop()
        elif command == 'version':
            self.set_header('Content-Type', 'application/json')
            rc['info'] = 'now version not supported!'
            rc['result'] = 'err'
            self.write(rc)
        elif command =='services':
            self.set_header('Content-Type', 'application/json')
            self.write(_service)

def main():
    try:
        tornado.options.parse_command_line()
        application = tornado.web.Application([
            url(r"/", MainHandler),
            url(r"/recording/cmd",CmdHandler),
            url(r"/recording/help", HelpHandler),
            url(r"/recording/internal",InternalHandler),
        ])

        global _rcmd
        _rcmd = RecordingCommand()
        global _class_schedule
        _class_schedule = Schedule(None)
        _class_schedule._analyse_json()

        application.listen(10006)

        start_card_server()

        global rh
        sds = [{'type':'recording','id':'recording','url':'http://<ip>:10006/recording'}]
        rh = RegHt(sds)

        global _ioloop
        _ioloop = IOLoop.instance()
        log_info('start service ！')
        _ioloop.start()

    except Exception as error:
        log_debug(str(error))
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
    else:
        log_info('The program is already running！')
