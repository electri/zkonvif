#!/usr/bin/python
# coding: utf-8
#
# @file: RecordServer.py
# @date: 2015-02-25
# @brief:
# @detail:
#
#################################################################

import sys, time, os, platform
import threading, Queue
import json
import CommonHelper
import cardlive_log

from socket import *
from functools import wraps
from tornado.web import *
from tornado.ioloop import IOLoop
from tornado.gen import *
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
from common.uty_log import log

_uname = platform.uname()[0]

# 必须设置工作目录 ...
os.chdir(os.path.dirname(os.path.abspath(__file__)))
_service = {"complete":False,"ids":[]}

def _param(req, key):
    if key in req.request.arguments:
        return req.request.arguments
    else:
        return None

_utils = None
_rcmd = None
_class_schedule = None
rh = None
_ioloop = None # 用于支持外面的结束 ...
_tokens = load_tokens('../common/tokens.json')


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Use the /recording/help for more help !")

class HelpHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('help.html')

def run_async(func):
	@wraps(func)
	def async_func(*args, **kwargs):
		f = threading.Thread(target = func, args = args, kwargs = kwargs)
		f.start()
		return f
	return async_func

class CmdHandler(tornado.web.RequestHandler):
    def get(self, token, service_id):
        self.__asy_cmd(token, service_id)

    @asynchronous
    @coroutine
    def __asy_cmd(self, token, service_id):
        rc = yield Task(self.__asy_cmd0, token=token, service_id=service_id)
        self.write(str(rc))
        self.set_header('Content-Type', 'application/json')
        self.finish()

    @run_async
    def __asy_cmd0(self, callback, token, service_id):
        rc={}
        rc['result'] = 'ok'
        rc['info'] = ''
        ip = ''
        hosttype = None
        mac = ''
        global _tokens

        if token == '0':
            ip= '127.0.0.1'
            hosttype = 'x86'
            mac = _utils.mymac()
            print 'mac is', mac
        else:
            if token not in _tokens:
                rc['result'] = 'error'
                rc['info'] = 'the %sth host does not exit'%token
                callback(rc)
                return
            else:
                hosttype = _tokens[token]['hosttype']
                mac = _tokens[token]['mac']
                ip = _tokens[token]['ip']
                #print hosttype, mac, ip
                #ip_port = get_private_from_tokens(token,service_id,'recording',_tokens)
                #ip = ip_port['target_ip']

        cmd = self.get_argument('RecordCmd','nothing')        


        if cmd == 'RtspPreview':
            rc = _rcmd.preview(ip,hosttype)
        elif cmd == 'CardLiveLog':
            if ip == '127.0.0.1':
                rc = cardlive_log.cardlive_log()
        elif cmd == 'UpdateClassSchedule':
            rc = _class_schedule.analyse_json(ip,mac)
        elif cmd == 'RTMPLiving':
            rc = StartLiving(ip, mac, hosttype)
        else:
            args = (self.request.uri.split('?'))[1]
            rc=_rcmd.send_command(args,ip)

        try:
            # 记录所有收到的命令和执行结果
            cont ='token=%s, sid=%s, cmd=%s, result=%s, info=%s' % (token, service_id, cmd, rc['result'], rc['info']) 
            log(cont, project='recording', level=9)
        except:
            pass

        callback(rc)


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
            rc['info'] = 'recording'
            self.write(rc)

def make_app():
    return Application([
            url(r"/", MainHandler),
            url(r"/recording/([^\/]+)/([^\/]+)/cmd",CmdHandler), #这里的 url 格式，必须与 tokens.json 中对应起来
            url(r"/recording/help", HelpHandler),
            url(r"/recording/internal",InternalHandler),
        ])

def start():
    app = make_app()
    app.listen(10006)

    log('recording srv starting, using port 10006', project='recording', level = 3)

    global _rcmd
    _rcmd = RecordingCommand()

    global _utils
    _utils = zkutils()

    start_card_server()

    stype = 'recording'
    reglist = gather_sds('recording', '../common/tokens.json')

    if _uname == 'Windows':
        #处理本机, FIXME: 目前仅仅 windows 版本的需要支持本机注册 ...
        service_url = r'http://<ip>:10006/recording/0/recording'
        local_service_desc = {}
        local_service_desc['type'] = stype
        local_service_desc['id'] = 'recording'
        local_service_desc['url'] = service_url
        _utils = zkutils()
        mac = _utils.mymac()
        local_service_desc['mac'] = mac
        local_service_desc['ip'] = '127.0.0.1'
        
        reglist.append(local_service_desc)

    log('mac:%s, ip:%s' % (mac, _utils.myip()), project='recording', level = 3)

    global _class_schedule
    _class_schedule = Schedule(None)
    for reg in reglist:
        _class_schedule.analyse_json(reg['ip'],reg['mac'])
    _class_schedule.restart_rtmp_living()
    _class_schedule.set_recording_dir()
    del_dir_schedule()

    global rh
    rh = RegHt(reglist)

    global _ioloop
    _ioloop = IOLoop.instance()
    log('running ...', project='recording', level = 3)
    _ioloop.start()
    log('terminated!!!!!', project='recording', level=3)


if __name__ == '__main__':
    result = CommonHelper.is_running()
    if result == False:
        start()



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
