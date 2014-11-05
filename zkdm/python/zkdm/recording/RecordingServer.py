# coding: utf-8

from tornado.web import *
from tornado.ioloop import IOLoop
from tornado.gen import  *
from socket import *
import json

from RecordingCommand import RecordingCommand
from tornado.options import define, options


# 必须设置工作目录 ...
os.chdir(os.path.dirname(os.path.abspath(__file__)))
_service = {"state":"no complete","ids":[]}

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

        cmd = _param(self, 'RecordCmd')

        if cmd is None:
            cmd = _param(self,'MetaInfoCmd')

        if cmd is None:
            cmd = _param(self,'BroadCastCmd')

        if cmd is None:
            rc['result'] = 'err'
            rc['info'] = '"RecordCmd" MUST be supplied!'
            self.set_header('Content-Type', 'application/json')
            self.write(rc)
            return

        elif cmd=={'RecordCmd':['RtspPreview']}:
            rc = _rcmd.preview()
            self.write(rc)
            return

        else:
            print cmd
            args = (self.request.uri.split('?'))[1]
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
    _service['state']='complete'

    global _ioloop
    _ioloop = IOLoop.instance()
    _ioloop.start()

if __name__ == "__main__":
    main()
