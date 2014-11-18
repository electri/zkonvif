# coding: utf-8

from tornado.web import *
from tornado.ioloop import IOLoop
from tornado.gen import  *
import urllib, urllib2
import thread, time, sys
import socket
import json

from RecordingCommand import RecordingCommand
from tornado.options import define, options
from CardServer import start_card_server
sys.path.append('../')
from common.utils import zkutils
from common.reght import RegHt


# 必须设置工作目录 ...
os.chdir(os.path.dirname(os.path.abspath(__file__)))
_service = {"complete":False,"ids":[]}

def _param(req, key):
    if key in req.request.arguments:
        return req.request.arguments
    else:
        return None

_rcmd = None
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
        elif cmd == 'RTMPLiving':
            try:
                req = urllib2.Request('http://host:port/repeater/prepublish')
                data = {}
                _utils = zkutils()
                data['mac'] = _utils.mymac()
                data['name'] = 'Living1'
                data['type'] = 'rtmp'
                data = urllibb.urlencode(data)
                opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
                response = opener.open(req,data)
                response =response.read()
                url = response['content']['stream_address']

                urllib2.Request('http://127.0.0.1:10007/card/LivingS?url='+url)
                time.sleep(1)
                rc=_rcmd.send_command('RecordCmd=StartBroadCast')
                if rc['result'] == 'ok':
                    rc['info'] = url
                self.set_header('Content-Type', 'application/json')
                self.write(rc)
            except Exception as err:
                rc['result'] = 'error'
                rc['info'] = str(err)
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
            rh.join()
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
    
    global rh
    rh = RegHt('recording','recording','10006/recording')
    

if __name__ == "__main__":
    main()
