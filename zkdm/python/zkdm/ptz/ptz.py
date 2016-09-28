import time
import inspect
import sys 
import platform
import threading
from serial import *

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
ptzs = {}

class Ptz:
    def __init__(self, com, address = 1):
        self.__com = com
        self.__addr = address
        self.__get_addr_head()
        self.__y0 = 0x80 + (self.__addr << 4)
        self.__sr = None
        try:
            if self.__com not in ptzs:
                self.__sr = Serial(self.__com)
                self.__sr.timeout = 30
                ptzs[self.__com] = self.__sr
            else:
                self.__sr = ptzs[self.__com]

        # FIXME: better warning than current
        except OSError as e:
            print "{0}: {1}".format(self.__com, e.strerror)
            sys.exit()
        except serialutil.SerialException as e:
            if sys_name == 'Windows':
                if "(2," in e.message:
                    print "{0} doesn\'t exist".format(self.__com)
                elif "(5," in e.message:
                    print "{0} was already used by another process".format(self.__com)
                else:
                    print "other error: %s"%(e.message) 
            else:
                pass
        else:
            # FIXME: if many cameras are connected, usage???
            self.__sr.write(ADDRESS_SET)
            pass

        self.__sr.close()

    def __del__(self):
        if self.__sr != None:
            self.__sr.close()
            ptzs.pop(self.__com) 

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
        ba = bytearray()
        is_ack = False
        s = self.__sr.read(1)
        while True:
            if s != '':
                ba.append(s)
                if s == '\xFF':
                    is_ack = self.__is_cmd_str(ba, v)				
                    if is_ack:					
                        break
                    else:
                        err_s = self.__error_type(ba)
                        if err_s != '':
                            print err_s
                            break
                        if s[0] == 0x88:
                            print 'broadcast'
                            break
                        ba = bytearray()
                        s = self.__sr.read(1)
                else:
                    s = self.__sr.read(1)

            else:
                break
        print 'yes: ', is_ack
        return is_ack

    def __recv_ack_packet(self):
        is_ack = self.__is_cmd_return(4)
        if is_ack == False:
            print 'return ack error'
        return is_ack
    
    def __recv_complete_packet(self):
        is_complete = self.__is_cmd_return(5)
        if is_complete == False:
            print 'return completion error'
            return False
        return is_complete

    def __recv_cmd_packet_with_blocked(self):
        return self.__recv_ack_packet() and \
                self.__recv_complete_packet()

    def __recv_cmd_packet(self):
        is_ack = self.__recv_ack_packet()
        return is_ack

    def left(self, vv):
        LEFT[4] = vv
        self.__sr.open()
        if __debug__:
            self.__sr.write(LEFT)
            v = self.__recv_cmd_packet()         
        else:
            self.__test_send_recv(LEFT)
        self.__sr.close()
        return v

    def right(self, vv):
        RIGHT[4] = vv
        self.__sr.open()
        if __debug__:
            self.__sr.write(RIGHT)
            v =  self.__recv_cmd_packet()
        else:
            self.__test_send_recv(RIGHT)
        self.__sr.close()
        return v

    def up(self, ww):
        UP[5] = ww
        self.__sr.open()
        if __debug__:
            self.__sr.write(UP)
            v = self.__recv_cmd_packet()
        else:
            self.__test_send_recv(UP)
        self.__sr.close()
        return v

    def down(self, ww):
        DOWN[5] = ww
        self.__sr.open()
        if __debug__:
            self.__sr.write(DOWN)
            v = self.__recv_cmd_packet()    
        else:
            self.__test_send_recv(DOWN)
        self.__sr.close()

    def __encode_para(self, para):
        paras = [0, 0, 0, 0]
        paras[0] = para >> 12 & 0x0F
        paras[1] = para >> 8 & 0x0F
        paras[2] = para >> 4 & 0x0F
        paras[3] = para & 0x0F
        return paras 
        
    def set_pos(self, y_para, z_para, vv, ww):
        ABSOLUTE_POS[4] = vv
        ABSOLUTE_POS[5] = ww
        y_paras = self.__encode_para(y_para)
        ABSOLUTE_POS[6:10] = y_paras

        z_paras = self.__encode_para(z_para)
        ABSOLUTE_POS[10:14] = z_paras

        if __debug__:
            self.__sr.write(ABSOLUTE_POS)
            return self.__recv_cmd_packet()
        else:
            self.__test_send_recv(ABSOLUTE_POS)

    def set_relative_pos(self, y_para, z_para, vv, ww):
        RELATIVE_POS[4] = vv
        RELATIVE_POS[5] = ww
        y_paras = self.__encode_para(y_para)
        RELATIVE_POS[6:10] = y_paras

        if __debug__:
            z_paras = self.__encode_para(z_para)
            RELATIVE_POS[10:14] = z_paras
            self.__sr.write(RELATIVE_POS)
            return self.__recv_cmd_packet()
        else:
            self.__test_send_recv(RELATIVE_POS)

    def set_pos_with_blocked(self, y_para, z_para, vv, ww):
        ABSOLUTE_POS[4] = vv
        ABSOLUTE_POS[5] = ww
        y_paras = self.__encode_para(y_para)
        ABSOLUTE_POS[6:10] = y_paras

        if __debug__:
            z_paras = self.__encode_para(z_para)
            ABSOLUTE_POS[10:14] = z_paras

            self.__sr.write(ABSOLUTE_POS)
            return self.__recv_cmd_packet_with_blocked()
        else:
            self.__test_send_recv(ABSOLUTE_POS)


    def set_zoom(self, z_para):
        z_paras = self.__encode_para(z_para)
        ZOOM_SET[4:8] = z_paras
        if __debug__:
            self.__sr.write(ZOOM_SET)
            return self.__recv_cmd_packet()
        else:
            self.__test_send_recv(ZOOM_SET)

    def set_zoom_with_blocked(self, z_para):
        z_paras = self.__encode_para(z_para)
        ZOOM_SET[4:8] = z_paras
        if __debug__:
            self.__sr.write(ZOOM_SET)
            return self.__recv_cmd_packet_with_blocked()
        else:
            self.__test_send_recv(ZOOM_SET)

    def stop(self):
        if __debug__:
            self.__sr.write(STOP)
            return self.__recv_cmd_packet()
        else:
            self.__test_send_recv(STOP)

    def zoom_tele(self, para):
        tz = 0x20 | para
        ZOOM_TEL[4] = tz
        if __debug__:
            self.__sr.write(ZOOM_TEL)
            return self.__recv_cmd_packet()
        else:
            self.__test_send_recv(ZOOM_TEL)

    def zoom_wide(self, para):
        wz = 0x30 | para       
        ZOOM_WIDE[4] = wz
        if __debug__:
            self.__sr.write(ZOOM_WIDE)
            return self.__recv_cmd_packet()
        else:
            self.__test_send_recv(ZOOM_WIDE)

    # note: it must be called twice
    def zoom_stop(self):
        if __debug__:
            self.__sr.write(ZOOM_STOP)
            return self.__recv_cmd_packet()
        else:
            self.__test_send_recv(ZOOM_STOP)

    def preset_clear(self, z):
        MEMORY_RESET[5] = z
        if __debug__:
            self.__sr.write(MEMORY_RESET)
            return self.__recv_cmd_packet()
        else:
            self.__test_send_recv(MEMORY_RESET)

    def preset_set(self, z):
        MEMORY_SET[5] = z
        if __debug__:
            self.__sr.write(MEMORY_SET)
            return self.__recv_cmd_packet()
        else:
            self.__test_send_recv(MEMORY_SET)

    def preset_call(self, z):
        MEMORY_CALL[5] = z
        if __debug__:
            self.__sr.write(MEMORY_CALL)
            return self.__recv_cmd_packet()
        else:
            self.__test_send_recv(MEMORY_CALL)

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
        s = self.__sr.read(1)
        while s != '':
            bas['ba'].append(s)
            if s == '\xFF':
                ipacket = self.__is_packet(bas['ba'])
                if (ipacket):
                    break
                else:
                    bas['ba'] = bytearray()
                    s = self.__sr.read(1)
            else:
                s = self.__sr.read(1)
        return ipacket 

    def get_paras(self):
        rt = []
        ipacket = False
        ba = bytearray()
        s = self.__sr.read(1)
        while s != '':
            if __debug__ != True:
                print s
            ba.append(s)
            if s == '\xFF':
                ipacket = self.__is_packet(ba)
                if (ipacket):
                    break
                else:
                    ba = bytearray()
                    s = self.__sr.read(1)
            else:
                s = self.__sr.read(1)

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

    def get_pos(self, kwargs = {'x':0, 'y':0}):
        self.__sr.flushInput()
        self.__sr.write(POS_INFO) 
        rt = self.get_paras()
        if len(rt) == 2:
            kwargs['x'] = self.__to_short_int(rt[0])
            kwargs['y'] = self.__to_short_int(rt[1])
            return True
        else:
            return False
             
    def get_zoom(self, kwargs = {'z':0}):            
        self.__sr.flushInput()
        self.__sr.write(ZOOM_INFO)
        rt = self.get_paras()
        if len(rt) == 1:
            kwargs['z'] = self.__to_short_int(rt[0])
            return True
        else:
            return False

    def read(self):
        while True:
            time.sleep(1)
            n = self.__sr.inWaiting()
            if n is not  0:
                ba = self.__sr.read(n)

                for i in range(n):
                    print hex(ord(ba[i]))
            break

    ''' usage for testing ptz'''
    def pos_reset(self):
        self.__sr.write(POS_RESET)
        return self.__recv_cmd_packet()

    def __test_send_recv(self, ba):
        print '===function: %s'%(inspect.stack()[1][3])    
        self.__sr.write(ba)
        beg = time.time()
        s = self.__sr.read(1)
        print 'all inWaiting: ', self.__sr.inWaiting() + 1
        len = self.__sr.inWaiting()
        s = s + self.__sr.read(len)
        ba = bytearray(s)
        print '\t value: ', self.__decode_ba(ba)
        print '\t reading time: ', time.time() - beg
        print '#####function %s over'%(inspect.stack()[1][3])
            

    def raw(self, value, mode, bas= None):
        self.__sr.write(value)
        if mode == 'ack':
            is_ack = self.__recv_cmd_packet()
            return is_ack 
        elif mode == 'complete':
            is_complete = self.__recv_cmd_packet_with_blocked()
            return is_complete
        elif mode == 'info':
            ipacket = self.__get_info(bas)
            return ipacket
        else:
            return False

    def mouse_trace(self, hvs, vvs, sx, sy, paras ={'s':0, 'hva':0, 'vva':0}):
        zooms ={}
        if self.get_zoom(zoom) != True:
            return -1;
        zs = self.ext_get_scales(paras['s'], zooms)
        hva = paras['hva'] / zs
        vva = paras['vva'] / zs

        h_rpm = int(hva*(hvs-0.5) / 0.075)
        v_rpm = int(vva*(0.5-vvs) / 0.075)

        return ptz_set_relative_pos(h_rpm, v_rpm, sx, sy)
          
    def ext_get_scales(self, string, zs = {'z':-1}):
        if zs['z'] < 0: 
            if (self.get_zoom(zs) < 0):
                return 1.0;            
        else:
            zm = zs['z']
            return round(0.00399466*zm**3 - 0.08866182*zm**2 + 0.64376676*zm*1 + 0.92906087) 

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
    if len(sys.argv) < 2 \
            or sys.argv[1] == "-help":
        sys.exit("usage: {0} COMX".format(sys.argv[0]))
    com = sys.argv[1]
    ptz = Ptz(com) 

