# coding: utf-8

from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application, url
from ctypes import *
import re, sys
import json, io, os
import logging
import inspect
from ptz import Ptz
sys.path.append('../')
from common.KVConfig import KVConfig

os.chdir(os.path.dirname(os.path.abspath(__file__)))
_all_config = json.load(io.open('./config.json', 'r', encoding='utf-8'))
        
def load_ptz(ptz_params):
    ptz = {'angles': None, 'physical': None}
    
    if 'extent' in ptz_params['config']:
        cfgfile = ptz_params['config']['extent'].encode('ascii')
        print 'open with cfg:' , cfgfile 
        cfg = KVConfig(cfgfile)
        com_name = cfg.get('ptz_serial_name')
        address = cfg.get('ptz_addr')
        angles = {'hva': float(cfg.get('hva')), 'vva': float(cfg.get('vva'))}
        ptz['angles'] = angles
        if com_name != '':
            ptz['physical'] = Ptz(com_name, int(address))
    else:
        serial = ptz_params['config']['serial']
        addr = ptz_params['config']['addr']

        print 'open ptz: ' , serial, 'addr: ', addr 
        ptz['physical'] = serial.encode('ascii'), int(addr)
    return ptz

def load_all_ptzs():
    ptzs_config = _all_config['ptzs']
    ret = {}
    for e in ptzs_config:
        ret[e['name']] = load_ptz(e)
    return ret

_all_ptzs = load_all_ptzs()

class HelpHandler(RequestHandler):
    def get(self):
        self.render('help.html')

class GetConfigHandler(RequestHandler):
    def get(self, path):
        cfg = self.__load_config()
        self.write(cfg)

    def __load_config(self):
        return { 'result':'ok', 'info':'', 'value': { 'type': 'list', 'data': _all_config['ptzs'] } }

class ControllingHandler(RequestHandler):
    def get(self, name, method):
        if _all_ptzs[name]['physical'] == None:
            self.write({'result': 'err', 'info': 'ptz {0} doesn\'t exist'.format(name)})
        else:
            ret = self.__exec_ptz_method(name, method, self.request.arguments)
            self.write(ret)

    def __exec_ptz_method(self, name, method, params):
        global _all_ptzs
        if name in _all_ptzs:
            ptz = _all_ptzs[name]
            if ptz:
                if method == 'mouse_trace':
                    params.update(ptz['angles'])
                print method
                return getattr(ptz['physical'], method)(params)
            else:
                return { 'result':'error', 'info':'ptz config failure' }
        else:
            return { 'result':'error', 'info':name + ' NOT found' }



def make_app():
    return Application([
            url(r'/ptz/help', HelpHandler),
            url(r"/ptz/config(/?)", GetConfigHandler),
            url(r'/ptz/([^\/]+)/([^\?]+)', ControllingHandler),
            ])


def main():
    app = make_app()
    app.listen(10003)
    IOLoop.current().start()

if __name__ == '__main__':
    main()    


