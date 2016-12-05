#!coding:utf-8
import time
import inspect
import sys 
import platform
import threading
import json
from serial import *

#XXXX: set adderss 出现问题，中间要停顿一下才行（譬如打印）...

sys_name = platform.system()

class Ptz:
    def __init__(self, com, address = 1):
        with open(".ptz.conf", "r") as fp: 
            cfg = json.loads(fp) 
        self.__cmds = cfg['cmds']
        self.__rets = cfg['rets']
        self.__openStates = cfg['openStates']
        self.__com = com
        self.__addr = address
        self.__get_addr_head()
        self.__y0 = 0x80 + (self.__addr << 4)
        self.__is_address = True 
        self.__serial = Serial(timeout=30)
        self.__serial.setPort(self.__com)

    def close(self):
        self.__serial.close()

    def __open(self):
        i = 0
        while not opened and i < 3:
            try:
                self.__serial.open()
        
            except SerialException as e:
                if 'WindowsError(2'in e.message:
                    open_id = -1
                elif 'WindowsError(5' in e.message:
                    open_id = -2 
                else:
                    open_id = -3
 
                time.sleep(25)
                i = i + 1
            else:
                open_id = 0

        return opened
                
    def __get_addr_head(self):
        hr = 0x80 + self.__addr
        for e in self.__cmds:
            e[0] = hr

    def __is_cmd_id(self, ba, v):
        if len(ba) == 3 \
            and ba[0] == self.__y0 \
            and ba[1] >> 4 == v \
            and ba[2] == 0xFF:
            if v == 4:
                return 0
            elif v == 5:
                return 1
            else:
                return -7
        elif ba == bytearray('\x88\x30\x02\xff'):
            return 2
        else:
            return -7

    def __error_id(self, ba):
        ret = -7
        if len(ba) == 4 \
            and ba[0] == self.__y0 \
            and ba[1] >> 4 == 6 \
            and ba[3] == 0xFF:
            if ba[2] == 0x02:
                ret  = -2 
            elif ba[2] == 0x03:
                ret = -3 
            elif ba[2] == 0x04:
                ret = -4 
            elif ba[2] == 0x05:
                ret  = -5 
            elif ba[2] == 0x41:
                ret = -6 
            else:
                pass
        return ret 
    
    def DEBUG(s):
        '''Print string converting from byte ...'''
        if __debug__ != True:
            print s.encode('hex')

    def __response(self, v):
        ba = bytearray()
        ret_id = -7
        s = self.__serial.read(1)
        while True:
            if s != '':
                ba.append(s)
                if s == '\xFF':
                    ret_id = self.__is_cmd_id(ba, v)                
                    if ret_id == 0 or ret_id == 1:                    
                        break
                    else:
                        ret_id = self.__error_id(ba)
                        if ret_id != -7:
                            break
                        length = len(ba)
                        for i in range(length):
                            ba.pop()
                        s = self.__serial.read(1)
                else:
                    s = self.__serial.read(1)

            else:
                ret_id = -1
                break

        caller = inspect.stack()[1][3]
        return {'return': self.__rets['result'], \
            'info': 'function ' + caller +' ' \
                + self.__rets['info']}

    def __communicate(cmd_protocal):
        open_id = self.__open()
        ots = self.__openstates[open_id]
        if open_id  != 0:
            v = {'result': ots['result'], \
                'info': self.__com + ' ' + ots['info'],}
        else:
            self.__serial.write(cmd_protocal)
            v = self.__is_cmd_return(4)         
            self.close()
        return v

 
    def __communicate_blocked(cmd_protocal):
        self.__open()
        self.__serial.write(ABSOLUTE_POS)
        ack = self.__is_cmd_return(4)
        complete = self.__is_cmd_return(5)
        self.close()
        if ack['result'] == 'ok' \
            and complete['result'] == 'ok':
            return complet 
        elif ack['result'] == 'ok' \
            and complete['result'] == 'err':
            return {'return': 'err', 'info': 'ack succeeds and comeplet fails'}
        elif ack['result'] == 'err' \
            and complete['result'] == 'ok':
            return {'result': 'err', 'info': 'ack fails and complete succeeds'}
        else:
            return {'result': 'err', 'info': 'ack fails and complete failes'}
       
    def right(self, params):
        vv = 0
        if 'speed' in params:
            vv  = int(params['speed'][0])
        RIGHT = bytearray(self.__cmds['right'])
        RIGHT[4] = vv
        return  self.__communicate(RIGHT)

    def up(self, params):
        ww = 0
        if 'speed' in params:
            ww  = int(params['speed'][0])
        UP = bytearray(self.__cmds['up'])
        UP[5] = ww
        return self.__communicate(UP)

    def down(self, params):
        ww = 0
        if 'speed' in params:
            ww  = int(params['speed'][0])
        DOWN = bytearray(self.__cmds['down'])
        DOWN[5] = ww
        return self.__communicate(DOWN)

    def __encode_para(self, para):
        paras = [0, 0, 0, 0]
        paras[0] = para >> 12 & 0x0F
        paras[1] = para >> 8 & 0x0F
        paras[2] = para >> 4 & 0x0F
        paras[3] = para & 0x0F
        return paras 
        
    def set_pos(self, params):
        # only return ack , no comepletion
        ABSOLUTE_POS = bytearray(self.__cmds['absolute_pos'])
        x = 0
        if 'x' in params:
            x = int(params['x'][0])
        ABSOLUTE_POS[6:10] = self.__encode_para(x)

        y = 0
        if 'y' in params:
            y = int(params['y'][0])
        ABSOLUTE_POS[10:14] = self.__encode_para(y)

        sx = 30
        if 'sx' in params:
            sx = int(params['sx'][0])
        ABSOLUTE_POS[4] = sx

        sy = 30
        if 'sy' in params:
            sy = int(params['sy'][0])
        ABSOLUTE_POS[5] = sy

        return self.__communicate(ABSOLUTE_POS)
        
    def set_rpos(self, params):
        RELATIVE_POS = bytearray(self.__cmds['relative_pos'])
        x = 0
        if 'x' in params:
            x = int(params['x'][0])
        RELATIVE_POS[6:10] = self.__encode_para(x)

        y = 0
        if 'y' in params:
            y = int(params['y'][0])
        RELATIVE_POS[10:14] = self.__encode_para(y)

        sx = 30
        if 'sx' in params:
            sx = int(params['sx'][0])
        RELATIVE_POS[4] = sx

        sy = 30
        if 'sy' in params:
            sy = int(params['sy'][0])
        RELATIVE_POS[5] = sy

        return self.__communicate(RELATIVE_POS)

    def set_pos_blocked(self, params):
        x = 0
        if 'x' in params:
            x = int(params['x'][0])
        ABSOLUTE_POS[6:10] = self.__encode_para(x)

        y = 0
        if 'y' in params:
            y = int(params['y'][0])
        ABSOLUTE_POS[10:14] = self.__encode_para(y)

        sx = 30
        if 'sx' in params:
            sx = int(params['sx'][0])
        ABSOLUTE_POS[4] = sx

        sy = 30
        if 'sy' in params:
            sy = int(params['sy'][0])
        ABSOLUTE_POS[5] = sy

        return self.__communicate_blocked(ABSOLUTE_POS) 

    def set_zoom(self, params):
        ZOOM_SET = bytearray(self.__cmds['zoom_set'])
        z = 0
        if 'z' in params:
            z = int(params['z'][0])
        z_paras = self.__encode_para(z)
        ZOOM_SET[4:8] = z_paras
        return self.__communicate(ZOOM_SET)
        

    def set_zoom_blocked(self, params):
        z = 0
        if 'z' in params:
            z = int(params['z'][0])
        z_paras = self.__encode_para(z)
        ZOOM_SET[4:8] = z_paras
        return self.__communicate_blocked(ZOOM_SET)
                
    def stop(self, params={}):
       STOP = bytearray(self.__cmds['stop'])
       return self.__communicate(STOP)

    def zoom_tele(self, params):
        ZOOM_TELE = bytearray(self.__cmds['zoom_tele'])
        speed = 1
        if 'speed' in params:
            speed = int(params['speed'][0])
        tz = 0x20 | speed
        ZOOM_TELE[4] = tz
        return self.__communicate(ZOOM_TELE) 

    def zoom_wide(self, params):
        ZOOM_WIDE = bytearray(self.__cmds['zoom_wide'])
        speed = 1
        if 'speed' in params:
            speed = int(params['speed'][0])
        wz = 0x30 | speed      
        ZOOM_WIDE[4] = wz
        return self.__communicate(ZOOM_WIDE)

    def zoom_stop(self, params={}):
        # note: it must be called twice
        ZOOM_STOP = bytearray(self.__cmds['zoom_stop'])
        return self.__communicate(ZOOM_STOP)
        
    def preset_clear(self, params):
        MEMORY_RESET = bytearray(self.__cmds['memery_reset'])
        if 'id' in params:
            z  = int(params['id'][0])
        else:
            return {'result': 'err',  'info': 'id dosn\'t be set'}

        MEMORY_RESET[5] = z
        return self.__communicate(MEMORY_RESET) 

    def preset_save(self, params):
        MEMORY_SET = bytearray(self.__cmds['memory_set'])
        if 'id' in params:
            z  = int(params['id'][0])
        else:
            return {'result': 'err', 'info': 'id dosn\'t be set'}
        MEMORY_SET[5] = z
        return self.__communicate(MEMORY_SET) 

    def preset_call(self, params):
        MEMORY_CALL = bytearray(self.__cmds['memory_call'])
        if 'id' in params:
            z  = int(params['id'][0])
        else:
            return {'result': 'err', 'info': 'id dosn\'t be set' }
        MEMORY_CALL[5] = z
        return self.__communicate(MEMORY_CALL) 

    def __is_packet(self, ba):
        length = len(ba)
        if (length-3)%4 == 0 \
            and ba[0] == self.__y0 \
            and ba[1] == 0x50 \
            and ba[-1] == 0xFF:
            return True
        else:
            return False

    def __decode_paras(self, paras, n):
        return  paras[n] << 12 | paras[n+1] << 8 | paras[n+2] << 4 | paras[n+3]

    def get_paras(self):
        rt = []
        ipacket = False
        ba = bytearray()
        s = self.__serial.read(1)
        while s != '':
            if __debug__ != True:
                print s.encode('hex') 
            ba.append(s)
            if s == '\xFF':
                ipacket = self.__is_packet(ba)
                if (ipacket):
                    break
                else:
                    ba = bytearray()
                    s = self.__serial.read(1)
            else:
                s = self.__serial.read(1)

        if ipacket  == True:
            length = len(ba) / 4
            for i in range(length):
             rt.append(self.__decode_paras(ba, 2 + 4 * i)) 

        return rt 

    def __to_short_int(self, v):
        '''Convert int to short int ...'''
        if (v & 0x8000 != 0):
            v = v & 0x7FFF
            v = ~v
            v = v & 0x7FFF
            v = v + 1
            v = -v
        return v

    def get_pos_zoom(self):
        '''Get position and zoom position ...'''
        pos = self.get_pos()
        zoom = self.get_zoom()

        if pos_ret['result'] == 'ok' \
            and zoom_ret['result'] == 'ok':
            return {'result': 'ok', 'info': '', \
                'value': {'type':'position_zoom', \
                    'data':{'x': pos['value']['data']['x'],'y':pos['value']['data']['y'],'z':zoom['value']['data']['z']}}}
        else:
            return {'result': 'err', 'info': 'ptz process error'}

    def get_pos(self, params={}):
        self.__open()
        self.__serial.flushInput()
        self.__serial.write(POS_INFO) 
        rt = self.get_paras()
        self.close()
        if len(rt) == 2:
            pos = {'x':0, 'y':0}
            pos['x'] = self.__to_short_int(rt[0])
            pos['y'] = self.__to_short_int(rt[1])
            return {'result': 'ok', 'info':'', 'value': {'type':'position', 'data': {'x': pos['x'], 'y': pos['y']}}}
        else:
            return {'result':'err', 'info':'ptz process error'}
             
    def get_zoom(self, params={}):            
        '''Get position zoom ... '''
        self.__open()
        self.__serial.flushInput()
        self.__serial.write(ZOOM_INFO)
        rt = self.get_paras()
        self.close()
        if len(rt) == 1:
            zoom = {'z':0}
            zoom['z'] = self.__to_short_int(rt[0])
            return {'result': 'ok', 'info': '', 'value': {'type':'zoom', 'data': {'z':zoom['z']}}}
        else:
            return {'result':'err', 'info':'ptz process error'}

    def pos_reset(self):
        ''' usage for testing ptz'''
        POS_RESET = bytearray(self.__cmds['pos_reset'])
        return self.__communicate(POS_RESET)

    def mouse_trace(self, params):
        ret  = self.ext_get_scales()
        if ret['result'] == 'err':
            return ret
        else:
            zs = ret['value']['data']['z']
            hva = params['hva'] / zs
            vva = params['vva'] / zs
            hvs = float(params['hvs'])
            vvs = float(params['vvs'])

            h_rpm = int(hva*(hvs-0.5) / 0.075)
            v_rpm = int(vva*(0.5-vvs) / 0.075)

            sx = int(params['sx'])
            sy = int(params['sy'])

            return set_rpos({'x': h_rpm, 'y': v_rpm, 'sx': sx, 'sy': sy})
          
    def ext_get_scales(self):
        '''Get ratio zoom ...'''
        X = [0x0000, 0x1606, 0x2151, 0x2860, 0x2CB5, 0x3060, 0x32D3, 0x3545, \
            0x3727, 0x38A9, 0x3A42, 0x3B4B, 0x3C85, 0x3D75, 0x3E4E, 0x3EF7, \
            0x3FA0, 0x4000] 

        Y = range(1, 19)

        p = [6.995e-23, -3.7984e-18, 8.116e-14, \
            -8.433e-10, 4.253e-06, -8.103e-03, 1.000e+00]
        zoom = self.get_zoom()
        if zoom['result'] == 'err':
            return zoom
        else:
            zm = zoom['value']['data']['z']
            popular_z = p[0] * zm ** 6 + p[1] * zm ** 5 + \
                p[2] * zm ** 4 + p[3] * zm ** 3 + \
                p[4] * zm ** 2 + p[5] * zm  + p[6]
            return {'result': 'ok', 'info': '', 'value': { 'type':'double', 'data': {'z': int(popular_z)}}}

    def __encode_ba(string):
        '''Convert string to bytearray ...'''
        length = len(string) / 2;
        ba = bytearray()
        for i in range(length):
            ch = string[i*2] + string[i*2+1]
            ba.append(int(ch, 16))

        return ba

    def __decode_ba(self, ba):
        '''Convert bytearray to string ...'''
        s = ''
        for i in range(len(ba)):
            ch = hex(ba[i])
            if len(ch) == 3:
                s += '0' + ch[2]
            else:
                s += ch[2] + ch[3]
        return s

if __name__ == '__main__':
    import time
    if len(sys.argv) < 2 \
            or sys.argv[1] == "-help":
        sys.exit("usage: {0} COMX".format(sys.argv[0]))
    com = sys.argv[1]
    ptz = Ptz(com)
    params = {'speed':['5']}
    ptz.down(params)
    time.sleep(5)
    ptz.stop()
