#!coding:utf-8
import time
import inspect
import sys 
import platform
import threading
from serial import *

#XXXX: set adderss 出现问题，中间要停顿一下才行（譬如打印）...

sys_name = platform.system()

# Address set broadcast
ADDRESS_SET = bytearray('\x88\x30\x01\xFF')

# pan tilt drive
UP = bytearray('\x8F\x01\x06\x01\x00\x00\x03\x01\xFF')
DOWN = bytearray('\x8F\x01\x06\x01\x00\x00\x03\x02\xFF')
LEFT= bytearray('\x8F\x01\x06\x01\x00\x00\x01\x03\xFF')
RIGHT= bytearray('\x8F\x01\x06\x01\x00\x00\x02\x03\xFF')
STOP = bytearray('\x8F\x01\x06\x01\x00\x00\x03\x03\xFF')
POS_RESET = bytearray('\x8F\x01\x06\x05\xFF')

ABSOLUTE_POS = bytearray('\x8F\x01\x06\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF')
RELATIVE_POS = bytearray('\x8F\x01\x06\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF')

# standard zoom drive
ZOOM_STOP = bytearray('\x8F\x01\x04\x07\x00\xFF')
ZOOM_TEL = bytearray('\x8F\x01\x04\x07\x20\xFF')
ZOOM_WIDE = bytearray('\x8F\x01\x04\x07\x30\xFF')
ZOOM_SET = bytearray('\x8F\x01\x04\x47\x00\x00\x00\x00\xFF') 

# cam memory
MEMORY_RESET = bytearray('\x8F\x01\x04\x3F\x00\x0F\xFF')
MEMORY_SET = bytearray('\x8F\x01\x04\x3F\x01\x0F\xFF')
MEMORY_CALL = bytearray('\x8F\x01\x04\x3F\x02\x0F\xFF')

# info
POS_INFO = bytearray('\x8F\x09\x06\x12\xFF')
ZOOM_INFO = bytearray('\x8F\x09\x04\x47\xFF')


RT = "======== return message ========\n" + \
    "ACK: z0 4y FF\n" + \
      "Command completion: z0 5y FF\n" + \
      "Information return: z0 50 ... FF\n" + \
      "Address set: z0 38 FF\n" + \
      "syntax error: z0 60 02 FF\n" + \
      "command buffer full: z0 60 03 FF\n" + \
      "command cancel: z0 60 04 FF\n" + \
      "No sockets: z0 60 05 FF\n" + \
      "Command not executable z0 60 41 FF\n" + \
      "==============================="

class Ptz:
    def __init__(self, com, address = 1):
        if __debug__ != True:
            print RT
        self.__com = com
        self.__addr = address
        self.__get_addr_head()
        self.__y0 = 0x80 + (self.__addr << 4)
        self.__is_address = True 
        self.__serial = Serial(timeout=30)
        self.__serial.setPort(self.__com)

    def __set_address(self):
        rt = self.__open_n()
        if rt != True:
            sys.exit('ptz set address fails')
        self.__serial.write(ADDRESS_SET)
        v = self.__is_cmd_return(4)
        self.close()
        return v

    def close(self):
        self.__serial.close()

    def __open_n(self):
        opened = False
        i = 0
        while not opened and i < 3:
            try:
                self.__serial.open()
        
            except SerialException as e:
                if 'WindowsError(5' in e.message:
                    print u'串口%s被另一个进程占用 ...'%(self.__com)
                elif 'WindowsError(2'in e.message:
                    print u'串口%s不存在'%(self.__com)
                else:
                    print u'串口%s不能被打开 ...'%(self.__com) 
 
                time.sleep(25)
                i = i + 1
            else:
                opened = True

        return opened
    
    def __open_begin(self):
        if not self.__is_address:
            self.__is_address = self.__set_address()
            if self.__is_address:
                print u'串口%s及其所连接设备正常启动 ...'%(self.__com)
            else:
                print u'设置地址失败 ...'
        rt = self.__open_n()
        if rt != True:
            print "serial {0} can\'t be opened".format(self.__com)
        return rt
                
    def __get_addr_head(self):
        hr = 0x80 + self.__addr

        UP[0] = hr
        DOWN[0] = hr
        LEFT[0] = hr
        RIGHT[0] = hr
        STOP[0] = hr
        POS_RESET[0] = hr
        ABSOLUTE_POS[0] = hr
        RELATIVE_POS[0] = hr

        ZOOM_TEL[0] = hr
        ZOOM_WIDE[0] = hr
        ZOOM_STOP[0] = hr
        ZOOM_SET[0] = hr

        MEMORY_RESET[0] = hr
        MEMORY_SET[0] = hr
        MEMORY_CALL[0] = hr
        POS_INFO[0] = hr
        ZOOM_INFO[0] = hr

    def __is_cmd_str(self, ba, v):
        if len(ba) == 3 \
            and ba[0] == self.__y0 \
            and ba[1] >> 4 == v \
            and ba[2] == 0xFF:
            return True
        elif ba == bytearray('\x88\x30\x02\xff'):
            return True
        else:
            return False

    def __error_type(self, ba):
        s = ''
        if len(ba) == 4 \
            and ba[0] == self.__y0 \
            and ba[1] >> 4 == 6 \
            and ba[3] == 0xFF:
            if ba[2] == 0x02:
                s = 'syntax error'
            elif ba[2] == 0x03:
                s = 'command buffer full'
            elif ba[2] == 0x04:
                s = 'command cancel'
            elif ba[2] == 0x05:
                s = 'no sockets'
            elif ba[2] == 0x41:
                s = 'command not executable'
            else:
                pass
        return s

                
    def __is_cmd_return(self, v):
        err_s = ''
        ba = bytearray()
        is_v = False
        if __debug__ != True:
            print '\n=== function: %s'%(inspect.stack()[1][3])    
            beg = time.time()
        s = self.__serial.read(1)
        while True:
            if s != '':
                if __debug__ != True:
                    print s.encode('hex') 
                ba.append(s)
                if s == '\xFF':
                    is_v = self.__is_cmd_str(ba, v)                
                    if is_v:                    
                        break
                    else:
                        err_s = self.__error_type(ba)
                        if err_s != '':
                            break
                        length = len(ba)
                        for i in range(length):
                            ba.pop()
                        s = self.__serial.read(1)
                else:
                    s = self.__serial.read(1)

            else:
                break
        if __debug__ != True:
            if err_s != '':
                print err_s
            if len(ba) == 3 and ba[1] >> 4 == 4:
                print 'ACK state: ', is_v
            elif len(ba) == 3 and ba[1] >> 4 == 5:
                print 'Command completion state: ', is_v
            elif len(ba) ==4 and ba[0] == 0x88 and ba[1] == 0x30 and \
                          ba[2] == 0X02 and ba[3] == 0xFF:
                print 'address set state: ', is_v
            else:
                pass
            print 'value: ', self.__decode_ba(ba)
            print 'reading time: ', time.time() - beg
            print '=== function %s over ...'%(inspect.stack()[1][3])
        return is_v

    def left(self, params):
        vv  =  0
        if 'speed' in params:
            vv  = int(params['speed'][0])
        LEFT[4] = vv
        print self.__decode_ba(LEFT)
        opened = self.__open_begin()
        if opened == False:
            return {'result': 'err', 'info': '{0} can\'t be opened'.format(self.__com)}
        self.__serial.write(LEFT)
        v = self.__is_cmd_return(4)         
        self.close()
        if v:
            return {'result': 'ok',  'info': 'ptz left completed'}
        else:
            return {'result': 'err', 'info': 'ptz left error'}

    def right(self, params):
        vv = 0
        if 'speed' in params:
            vv  = int(params['speed'][0])
        RIGHT[4] = vv
        self.__open_begin()
        print self.__decode_ba(RIGHT) 
        self.__serial.write(RIGHT)
        v =  self.__is_cmd_return(4)
        self.close()
        if v:
            return {'result': 'ok',  'info':'completed'}
        else:
            return {'result': 'err',  'info': 'ptz process error'}

    def up(self, params):
        ww = 0
        if 'speed' in params:
            ww  = int(params['speed'][0])

        UP[5] = ww
        self.__open_begin()
        self.__serial.write(UP)
        v = self.__is_cmd_return(4)
        self.close()
        if v:
            return {'result': 'ok',  'info': 'up completed'}
        else:
            return {'result': 'err',  'info': 'ptz up error' }

    def down(self, params):
        ww = 0
        if 'speed' in params:
            ww  = int(params['speed'][0])

        DOWN[5] = ww
        self.__open_begin()
        self.__serial.write(DOWN)
        v = self.__is_cmd_return(4)    
        self.close()
        if not self.__serial.isOpen():
            print 'down close'
        if v:
            return {'result': 'ok',  'info': 'down completed'}
        else:
            return {'result': 'err',  'info': 'ptz down error' }

    def __encode_para(self, para):
        paras = [0, 0, 0, 0]
        paras[0] = para >> 12 & 0x0F
        paras[1] = para >> 8 & 0x0F
        paras[2] = para >> 4 & 0x0F
        paras[3] = para & 0x0F
        return paras 
        
    def set_pos(self, params):
        # only return ack , no comepletion
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

        self.__open_begin()
        self.__serial.write(ABSOLUTE_POS)
        v = self.__is_cmd_return(4)
        self.close()
        if v:
            return {'result': 'ok', 'info': 'completed'}
        else:
            return {'result': 'err', 'info': 'ptz process error'}
        
    def set_rpos(self, params):
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

        self.__open_begin()
        self.__serial.write(RELATIVE_POS)
        v =  self.__is_cmd_return(4)
        self.close()

        if v:
            return {'result': 'ok', 'info': 'completed' }
        else:
            return { 'result': 'err', 'info': 'ptz process error' }

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

        self.__open_begin()
        self.__serial.write(ABSOLUTE_POS)
        is_ack = self.__is_cmd_return(4)
        is_complete = self.__is_cmd_return(5)
        self.close()
        if is_ack and is_complete:
            return {'return': 'ok', 'info':'completed'}
        else:
            return {'return': 'err', 'info': 'ptz process error'}

    def set_zoom(self, params):
        z = 0
        if 'z' in params:
            z = int(params['z'][0])
        z_paras = self.__encode_para(z)
        ZOOM_SET[4:8] = z_paras
        self.__open_begin()
        self.__serial.write(ZOOM_SET)
        v =  self.__is_cmd_return(4)
        self.close()
        if v:
            return {'return': 'ok',  'info':'completed'}
        else:
            return {'return': 'err',  'info': 'ptz process error'}


    def set_zoom_blocked(self, params):
        z = 0
        if 'z' in params:
            z = int(params['z'][0])
        z_paras = self.__encode_para(z)
        ZOOM_SET[4:8] = z_paras
        self.__open_begin()
        self.__serial.write(ZOOM_SET)
        is_ack = self.__is_cmd_return(4)
        is_complete = self.__is_cmd_return(5)
        self.close()
        if is_ack and is_complete:
            return {'return': 'ok',  'info':'completed'}
        else:
            return {'return': 'err',  'info': 'ptz process error'}
        
    def stop(self, params={}):
        self.__open_begin()
        self.__serial.write(STOP)
        v = self.__is_cmd_return(4)
        self.close()
        if v:
            return { 'result': 'ok', 'info':'completed' } 
        else:
            return { 'result': 'err', 'info': 'ptz process  error' }

    def zoom_tele(self, params):
        speed = 1
        if 'speed' in params:
            speed = int(params['speed'][0])
        tz = 0x20 | speed
        ZOOM_TEL[4] = tz
        self.__open_begin()
        self.__serial.write(ZOOM_TEL)
        v = self.__is_cmd_return(4)
        self.close()
        if v:
            return {'result': 'ok', 'info':'completed'}
        else:
            return {'result': 'err', 'info': 'ptz process error'}

    def zoom_wide(self, params):
        speed = 1
        if 'speed' in params:
            speed = int(params['speed'][0])
        wz = 0x30 | speed      
        ZOOM_WIDE[4] = wz
        self.__open_begin()
        self.__serial.write(ZOOM_WIDE)
        v =  self.__is_cmd_return(4)
        self.close()
        if v:
            return {'result': 'ok', 'info':'completed'}
        else:
            return {'result': 'err', 'info': 'ptz process error'}

    # note: it must be called twice
    def zoom_stop(self, params={}):
        self.__open_begin()
        self.__serial.write(ZOOM_STOP)
        v = self.__is_cmd_return(4)
        self.close()
        if v:
            return {'result': 'ok', 'info':'completed'}
        else:
            return {'result': 'err', 'info': 'ptz process error'}
        
    def preset_clear(self, params):
        if 'id' in params:
            z  = int(params['id'][0])
        else:
            return {'result': 'err',  'info': 'id dosn\'t be set'}

        MEMORY_RESET[5] = z
        self.__open_begin()
        self.__serial.write(MEMORY_RESET)
        v = self.__is_cmd_return(4)
        self.close()
        if v:
            return {'result': 'ok', 'info': 'completed'}
        else:
            return {'result': 'err', 'info': 'ptz proccess error'} 

    def preset_save(self, params):
        if 'id' in params:
            z  = int(params['id'][0])
        else:
            return {'result': 'err', 'info': 'id dosn\'t be set'}
        MEMORY_SET[5] = z
        self.__open_begin()
        self.__serial.write(MEMORY_SET)
        v = self.__is_cmd_return(4)
        self.close()
        if v:
            return {'result': 'ok', 'info': 'completed'}
        else:
            return {'result': 'err',  'info': 'ptz proccess error'}

    def preset_call(self, params):
        if 'id' in params:
            z  = int(params['id'][0])
        else:
            return {'result': 'err', 'info': 'id dosn\'t be set' }
        MEMORY_CALL[5] = z
        self.__open_begin()
        self.__serial.write(MEMORY_CALL)
        v = self.__is_cmd_return(4)
        self.close()
        if v:
            return {'result': 'ok', 'info': 'completed'}
        else:
            return {'result': 'err', 'info': 'ptz proccess error' }

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

    def __get_info(self, bas):
        ipacket = False
        bas['ba'] = bytearray()
        s = self.__serial.read(1)
        while s != '':
            bas['ba'].append(s)
            if s == '\xFF':
                ipacket = self.__is_packet(bas['ba'])
                if (ipacket):
                    break
                else:
                    bas['ba'] = bytearray()
                    s = self.__serial.read(1)
            else:
                s = self.__serial.read(1)
        return ipacket 

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
        if (v & 0x8000 != 0):
            v = v & 0x7FFF
            v = ~v
            v = v & 0x7FFF
            v = v + 1
            v = -v
        return v

    def get_pos_zoom(self):
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
        self.__open_begin()
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
        self.__open_begin()
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

    ''' usage for testing ptz'''
    def pos_reset(self):
        self.__open_begin()
        self.__serial.write(POS_RESET)
        v =  self.__is_cmd_return(4)
        self.close()
        return v

    def __raw(self, value, mode, bas= None):
        self.__open_begin()
        self.__serial.write(value)
        if mode == 'ack':
            is_ack = self.__is_cmd_return(4)
            self.close()
            return is_ack 
        elif mode == 'complete':
            is_ack = self.__is_cmd_return(4)
            is_complete = self.__is_cmd_return(5)
            self.close()
            return is_ack and is_complete
        elif mode == 'info':
            ipacket = self.__get_info(bas)
            self.close()
            return ipacket
        else:
            self.close()
            return False

    def raw(self, params):
        if 'value' in params and 'mode' in params:
            result = {}
            value = params['value'][0]
            ba = self.__encode_ba(value)
            mode = params['mode'][0]
            is_ret  = self.__raw(ba, mode, result)
            if  is_ret != True:
                return {'result': 'err', 'info': 'timeout'}
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
    
    '''
    ptz = Serial(port=com, baudrate=9600)
    if ptz.isOpen():
        print 'open'
    ptz.write(bytearray('\x81\x01\x06\x01\x09\x00\x02\x03\xFF'))
    time.sleep(5)
    ptz.write(bytearray('\x81\x01\x06\x01\x0A\x00\x01\x03\xFF'))
   ''' 
