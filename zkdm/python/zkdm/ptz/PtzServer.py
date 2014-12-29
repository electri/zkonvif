# coding: utf-8

from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application, url
from tornado import gen
from ctypes import *
import re, sys
import json, io, os
from PtzWrap import PtzWrap
sys.path.append('../')
from common.Log import Log
from common.uty_token import *
from common.reght import RegHt
import thread
import ArmPtz

import logging

_all_config = json.load(io.open('./config.json', 'r', encoding='utf-8'))
#_tokens = json.load(io.open('../common/tokens.json', 'r', encoding='utf-8'))
_tokens = load_tokens('../common/tokens.json')
logging.basicConfig(filename='ptz.log', filemode='w', level=logging.DEBUG)

def all_ptzs_config():
    ''' 返回配置的云台 ... '''
    return _all_config['ptzs']
        
def load_ptz(config):
    ''' 加载云台配置模块 '''
    ptz = {
        'name': config['name'],
        'serial': config['config']['serial'],
        'addr': config['config']['addr'],
        'ptz': None
    }

    if 'extent' in config['config']:
        ptz['cfgfile'] = config['config']['extent']

    # 此处打开 ...
    if True:
        is_ptz = False
        ptz['ptz'] = PtzWrap()
         # 来自 json 字符串都是 unicode, 需要首先转换为 string 交给 open 
        if 'cfgfile' in ptz:
            filename = ptz['cfgfile'].encode('ascii')
            print 'open with cfg:', filename
            is_ptz = ptz['ptz'].open_with_config(filename)
            logging.info('open with cfg: %s', filename)
            if is_ptz == False:
                logging.info('failure')    
            else:
                logging.info('succeed')
        else:
            print 'open ptz:', ptz['serial'], 'addr:', ptz['addr']
            is_ptz = ptz['ptz'].open(ptz['serial'].encode('ascii'), int(ptz['addr']))
        if not is_ptz:
            ptz['ptz'] = None    
    else:
        ptz['ptz'] = None
        print 'open failure'

    return ptz


def load_all_ptzs():
    ''' 加载所有云台模块 '''
    ptzs = all_ptzs_config()
    ret = {}
    for x in ptzs:
        ret[x['name']] = (load_ptz(x))

    return ret


# 这里保存所有云台
_all_ptzs = load_all_ptzs()

reglist = []
stype = 'ptz'
for e in _all_ptzs:
    if _all_ptzs[e]['ptz'] is not None:
        sid = e
        service_url= r'http://<ip>:10003/%s/0/%s'%(stype, sid)
        regunit = {'type': stype, 'id': sid, 'url': service_url}
        reglist.append(regunit)
  
reglist = reglist + gather_sds_from_tokens(_tokens, 'ptz')
rh = RegHt(reglist)

class HelpHandler(RequestHandler):
    ''' 返回 help 
         晕啊，必须考虑当前目录的问题 ...
    '''
    def get(self):
        self.render('help.html')



class GetConfigHandler(RequestHandler):
    ''' 返回云台配置 '''
    def get(self, path):
        cfg = self.__load_config()
        self.set_header('Content-Type', 'application/json')
        self.write(cfg)

    def __load_config(self):
        return { 'result':'ok', 'info':'', 'value': { 'type': 'list', 'data':all_ptzs_config() } }


from tornado.web import *

class ControllingHandler(RequestHandler):
    ''' 处理云台操作 '''
    @asynchronous
    def get(self, token, name, method):
        ''' sid 指向云台，method_params 为 method?param1=value1&param2=value2& ....
        '''
        print token, name, method
        thread.start_new_thread(self.callback, (token, name, method))

    def callback(self, token, name, method):
        ret = ''
        global _tokens
        if token == '0':
            ret = self.__exec_ptz_method(name, method, self.request.arguments)    
        else:
            if token not in _tokens:
                ret = {'result':'error', 'info': 'the %sth host does not exist'%token} 
            else:
                id_port = get_private_from_tokens(token, name, 'ptz', _tokens)
                # FIXME: 这里添加了是否找到 service id 的判断
                if 'ip' not in id_port:
                    ret = {'result': 'error', 'info': 'the service_id=%s NOT found' % name }
                else:
                    nm = name
                    if id_port['id'] is not '':
                        nm = id_port['id']
                    armcmd = ArmPtz.toArmStr(nm, method, self.request.arguments)
                    ret = ArmPtz.SendThenRecv(id_port['ip'], id_port['port'],armcmd)
        self.set_header('Constent-Type', 'application/json')
        self.write(ret)
        self.finish()

    def __exec_ptz_method(self, name, method, params):
        global _all_ptzs
        # print 'name:', name, ' method:', method, ' params:', params
        if name in _all_ptzs:
            if _all_ptzs[name]['ptz']:
                return _all_ptzs[name]['ptz'].call(method, params)
            else:
                return { 'result':'error', 'info':'ptz config failure' }
        else:
            return { 'result':'error', 'info':name + ' NOT found' }


# 为了支持 exit command
_ioloop = IOLoop.instance()


class InternalHandler(RequestHandler):
    def get(self):
        rc = {}
        rc['result'] = 'ok'
        rc['info'] = 'dispear'

        command = self.get_argument('command', 'nothing')
        print command
        if command == 'exit':
            rc['info'] = 'exit!!!'
            global rh     
            rh.join()
            global _ioloop
            _ioloop.stop()
            self.write(rc)
        elif command == 'version':
            rc['info'] = 'now version unsupported!!'
            rc['result'] = 'err'
            self.write(rc)

def make_app():
    return Application([
            url(r'/ptz/help', HelpHandler),
            url(r"/ptz/config(/?)", GetConfigHandler),
            url(r'/ptz/([^\/]+)/([^\/]+)/([^\?]+)', ControllingHandler),
            url(r'/ptz/internal', InternalHandler),
            ])

def main():
    app = make_app()
    app.listen(10003)
    _ioloop.start()
    # 此时说明结束 ...




if __name__ == '__main__':
    main()

