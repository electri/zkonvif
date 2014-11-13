# coding: utf-8

from tornado.web import *
from tornado.ioloop import IOLoop
from tornado.gen import  *
import urllib, urllib2
import thread, time
import socket
import json

from RecordingCommand import RecordingCommand
from tornado.options import define, options
from CardServer import start_card_server


# 必须设置工作目录 ...
os.chdir(os.path.dirname(os.path.abspath(__file__)))
_service = {"complete":False,"ids":[]}

def _param(req, key):
    if key in req.request.arguments:
        return req.request.arguments
    else:
        return None

_rcmd = None

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
        elif cmd == 'RTMPLiving':
            url = self.get_argument('RtmpUrl','nothing')
            urllib2.Request('http://127.0.0.1:10007/card/LivingS?url='+url)

            time.sleep(1)

            rc=_rcmd.send_command('RecordCmd=StartBroadCast')
            self.set_header('Content-Type', 'application/json')
            self.write(rc)

            return
        else:
            args = (self.request.uri.split('?'))[1]
            print args
            rc=_rcmd.send_command(args)
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



def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application([
        url(r"/", MainHandler),
        url(r"/recording/cmd",CmdHandler),
        url(r"/recording/help", HelpHandler),
        url(r"/recording/internal",InternalHandler),
    ])

    global _rcmd
    _rcmd = RecordingCommand()

    application.listen(10006)

    _service['ids'].append('recording')
    _service['complete'] = True

    start_card_server()

    global _ioloop
    _ioloop = IOLoop.instance()
    _ioloop.start()



if __name__ == "__main__":
    main()
