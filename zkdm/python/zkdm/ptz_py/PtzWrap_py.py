# coding: utf-8

import sys
import time
import platform, os
from ptz import Ptz
sys.path.append('../')
from common.KVConfig import KVConfig

class PtzWrap(object):
    ''' 封装 ptz.py 的调用
    '''
    def __init__(self):
        cpath = os.getcwd()
        tpath = os.path.dirname(os.path.abspath(__file__))
        os.chdir(tpath)
        self.__cfg = None
        self.__ptz = None
        os.chdir(cpath)

    def open(self, serial, address):
        self.__ptz = Ptz(serial, address)
        return True
            
  
    def open_with_config(self, cfg_filename):
        ''' 优先使用该方法，支持 mouse_track, ptz_ext_xxx '''
        self.__cfg = KVConfig(cfg_filename)
        com_name = self.__cfg.get('ptz_serial_name')
        address = self.__cfg.get('ptz_addr')
        if com_name != None and address != None:
            self.__ptz = Ptz(com_name, int(address)) 
            return (self.__ptz is not None)
        else:
            return False

    def close(self):
        if self.__ptz:
            self.__ptz = None

    
    def call(self, method, params):
        ''' 执行 method 命令，使用 params 作为参数 .tr..
        '''
        # TODO：应该检查参数 ... 
        ret = {'result':'ok', 'info':''}

        if method == 'stop':
            ret.update(self.stop())
        elif method == 'left':
            ret.update(self.left(params))
        elif method == 'right':
            ret.update(self.right(params))
        elif method == 'up':
            ret.update(self.up(params))
        elif method == 'down':
            ret.update(self.down(params))
        elif method == 'preset_save':
            ret.update(self.preset_save(params))
        elif method == 'preset_call':
            ret.update(self.preset_call(params))
        elif method == 'preset_clear':
            ret.update(self.preset_clear(params))
        elif method == 'get_pos':
            ret.update(self.get_pos())
        elif method == 'set_pos':
            ret.update(self.set_pos(params))
        elif method == 'set_rpos':
            ret.update(self.set_rpos(params))
        elif method == 'set_pos_blocked':
            ret.update(self.set_pos_blocked(params))
        elif method == 'get_zoom':
            ret.update(self.get_zoom())
        elif method == 'set_zoom':
            ret.update(self.set_zoom(params))
        elif method == 'set_zoom_blocked':
            ret.update(self.set_zoom_blocked(params))
        elif method == 'get_pos_zoom':
            ret.update(self.get_pos_zoom())
        elif method == 'zoom_tele':
            ret.update(self.zoom_tele(params))
        elif method == 'zoom_wide':
            ret.update(self.zoom_wide(params))
        elif method == 'zoom_stop':
            ret.update(self.zoom_stop())
        elif method == 'mouse_trace':
            ret.update(self.mouse_trace(params))
        elif method == 'ext_get_scales':
            ret.update(self.ext_get_scales())
        elif method == 'is_prepared':
            ret.update(self.is_prepared())
        elif method == 'raw':
            ret.update(self.raw(params))
        else:
            ret.update({'result':'error', 'info':'method NOT supported'})
        return ret

    def is_prepared(self):
        if not self.__ptz:
            return {'result':'error', 'info':'NO ptz'}
        else:
            r = self.__ptz.is_prepared()
            if r is 0:
                return { 'info': 'completed'}
            else:
                return { 'result':'error', 'info': 'NO ptz prepared'}

    def stop(self):
        if not self.__ptz:
            return {'result':'error', 'info':'NO ptz'}
        else:
            self.__ptz.stop()           
            return { 'info':'completed' }

    def left(self, params):
        if not self.__ptz:
            return {'result':'error', 'info':'NO ptz'}
        else:
            speed = 1
            if 'speed' in params:
                speed = int(params['speed'][0])
                
            self.__ptz.left(speed)
            return { 'info':'completed' }


    def right(self, params):
        if not self.__ptz:
            return {'result':'error', 'info':'NO ptz'}
        else:
            speed = 1
            if 'speed' in params:
                speed = int(params['speed'][0])
                
            self.__ptz.right(speed)
            return { 'info':'completed' }


    def up(self, params):
        if not self.__ptz:
            return {'result':'error', 'info':'NO ptz'}
        else:
            speed = 1
            if 'speed' in params:
                speed = int(params['speed'][0])
                
            self.__ptz.up(speed)
            return { 'info':'completed' }


    def down(self, params):
        if not self.__ptz:
            return {'result':'error', 'info':'NO ptz'}
        else:
            speed = 1
            if 'speed' in params:
                speed = int(params['speed'][0])
            self.__ptz.down(speed)
            return { 'info':'completed' }

    def preset_save(self, params):
        if not self.__ptz:
            return {'result':'error', 'info':'NO ptz'}
        else:
            if 'id' in params:
                id = int(params['id'][0])
                self.__ptz.preset_save(id)
                return {'info':'completed'}
            else:
                return {'result':'error', 'info':'NO liuwenen id'}
        
    def preset_call(self, params):
        if not self.__ptz:
            return {'result':'error', 'info':'NO ptz'}
        else:
            if 'id' in params:
                id = int(params['id'][0])
                self.__ptz.preset_call(id)
                return {'info':'completed'}
            else:
                return {'result':'error', 'info':'NO id'}


    def preset_clear(self, params):
        if not self.__ptz:
            return {'result':'error', 'info':'NO ptz'}
        else:
            if 'id' in params:
                id = int(params['id'][0])
                self.__ptz.preset_clear(id)
                return {'info':'completed'}
            else:
                return {'result':'error', 'info':'NO id'}            


    def get_pos(self):
        if not self.__ptz:
            return {'result':'error', 'info':'NO ptz'}
        else:
            pos = {} 
            if self.__ptz.get_pos(pos) == True:
                return { 'value': { 'type':'position', 'data': {'x': pos['x'], 'y': pos['y']} } }
            else:
                return { 'result':'error', 'info':'get_pos failure' }

    def get_pos_zoom(self):
            if not self.__ptz:
                return {'result':'error', 'info':'No PTZ'}
            else:
                pos = {}
                zoom = {}
                is_pos = self.__ptz.get_pos(pos)
                is_zoom = self.__ptz.get_zoom(zoom)
                
                if (is_pos==True) and (is_zoom==True):
                    return {'value': { 'type':'position', 'data': {'x': pos['x'], 'y': pos['y'], 'z': zoom['z']} } }
                else:
                    return {'result':'error', 'info':'No PTZ'}
            
    def ext_get_scales(self):
        if not self.__ptz:
            return { 'result':'error', 'info':'NO ptz' }
        else:
            return { 'value': { 'type':'double', 'data': self.__ptz.ext_get_scales(-1) } }

    def set_pos(self, params):
        if not self.__ptz:
            return {'result':'error', 'info':'NO ptz'}
        else:
            x = 0
            y = 0
            sx = 30
            sy = 30
            if 'x' in params:
                x = int(params['x'][0])
            if 'y' in params:
                y = int(params['y'][0])
            if 'sx' in params:
                sx = int(params['sx'][0])
            if 'sy' in params:
                sy = int(params['sy'][0])
                
            self.__ptz.set_pos(x, y, sx, sy)
            return { 'info':'completed' }

    def set_rpos(self, params):
        if not self.__ptz:
            return {'result':'error', 'info':'NO ptz'}
        else:
            x = 0
            y = 0
            sx = 30
            sy = 30
            if 'x' in params:
                x = int(params['x'][0])
            if 'y' in params:
                y = int(params['y'][0])
            if 'sx' in params:
                sx = int(params['sx'][0])
            if 'sy' in params:
                sy = int(params['sy'][0])
                
            self.__ptz.set_relative_pos(x, y, sx, sy)
            return { 'info':'completed' }

    def set_pos_blocked(self, params):
        if not self.__ptz:
            return {'result':'error', 'info':'NO ptz'}
        else:
            x = 0
            y = 0
            sx = 30
            sy = 30
            if 'x' in params:
                x = int(params['x'][0])
            if 'y' in params:
                y = int(params['y'][0])
            if 'sx' in params:
                sx = int(params['sx'][0])
            if 'sy' in params:
                sy = int(params['sy'][0])
                
            self.__ptz.set_pos_with_blocked(x, y, sx, sy)
            return { 'info':'completed' }
       
            
    def mouse_trace(self, params):
            if not self.__ptz:
                return {'return':'error', 'info':'NO ptz'}
            else:
                x = 0.0
                y = 0.0
                sx = 30
                sy = 30
                if 'x' in params:
                    x = float(params['x'][0])
                if 'y' in params:
                    y = float(params['y'][0])
                if 'sx' in params:
                    sx = int(params['sx'][0])
                if 'sy' in params:
                    sy = int(params['sy'][0])
                self.__ptz.mouse_trace(x, y, sx, sy)
                return {'info':'completed'}

    def get_zoom(self):
        if not self.__ptz:
            return {'result':'error', 'info':'NO ptz'}
        else:
            zoom = {} 
            if self.__ptz.get_zoom(zoom) == True:
                return {'value': { 'type':'position', 'data': {'z':zoom['z'] }}}
            else:
                return {'result':'error', 'info':'get_zoom failure' }


    def set_zoom(self, params):
        if not self.__ptz:
            return {'result':'error', 'info':'NO ptz'}
        else:
            z = 0
            if 'z' in params:
                z = int(params['z'][0])
            self.__ptz.set_zoom(z)
            return { 'info':'completed' }

    def set_zoom_blocked(self, params):
        if not self.__ptz:
            return {'result':'error', 'info':'NO ptz'}
        else:
            z = 0
            if 'z' in params:
                z = int(params['z'][0])
            self.__ptz.set_zoom_with_blocked(z)
            return { 'info':'completed' }


    def zoom_wide(self, params):
        if not self.__ptz:
            return {'result':'error', 'info':'NO ptz'}
        else:
            speed = 1
            if 'speed' in params:
                speed = int(params['speed'][0])
            self.__ptz.zoom_wide(speed)
            return {'info':'completed'}


    def zoom_tele(self, params):
        if not self.__ptz:
            return {'result':'error', 'info':'NO ptz'}
        else:
            speed = 1
            if 'speed' in params:
                speed = int(params['speed'][0])
            self.__ptz.zoom_tele(speed)
            return {'info':'complete'}


    def zoom_stop(self):
        if not self.__ptz:
            return {'result':'error', 'info':'NO ptz'}
        else:
            self.__ptz.zoom_stop()
            return {'info':'complete'}
   
    def __encode_ba(self, string):
        length = len(string) / 2;
        ba = bytearray()
        for i in range(length):
            ch = string[i*2] + string[i*2+1]
            ba.append(int(ch, 16))

        return ba

    def __decode_ba(self, ba):
        s = ''
        for i in range(len(ba)):
            ch = hex(ba[i])
            if len(ch) == 3:
                s += '0' + ch[2]
            else:
                s += ch[2] + ch[3]
        return s

    def raw(self, params):
            if not self.__ptz:
                return {'result':'error', 'info':'NO ptz'}
            else:
                if 'value' in params and 'mode' in params:
                    result = {}
                    value = params['value'][0]
                    ba = self.__encode_ba(value)
                    mode = params['mode'][0]
                    is_ret  = self.__ptz.raw(ba, mode, result)
                    if  is_ret != True:
                        return {'result': 'error', 'info': 'timeout'}
                    else:
                        if mode == 'info':
                            print '##########'
                            print result
                            s = self.__decode_ba(result['ba']) 
                            return {'result': 'ok', 'info': s} 
                        else:
                            return {'result': 'ok', 'info': ''}
                else:
                    return {'result':'error', 'info': 'no params'} 
