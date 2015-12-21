import sys 
import platform
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
            if "(2," in e.message:
                print "{0} doesn\'t exist".format(self.__com)
            elif "(5," in e.message:
                print "{0} was already used by another process".format(self.__com)
            else:
                pass
	
        else:
            # FIXME: if many cameras are connected, usage???
            self.__sr.write(ADDRESS_SET)
            pass

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
                        ba = bytearray()
                        s = self.__sr.read(1)
                else:
                    s = self.__sr.read(1)

            else:
                break

        return is_ack

    def __recv_ack_packet(self):
        is_ack = self.__is_cmd_return(4)
        if is_ack == False:
            print 'return ack error'
        return is_ack

    def __recv_cmd_packet(self):
        is_ack = self.__is_cmd_return(4)
        if is_ack == False:
            print 'return ack error'
            return False

        is_complete = self.__is_cmd_return(5)
        if is_complete == False:
            print 'return completion error'
            return False

        return True
       
    def left(self, vv):
        LEFT[4] = vv
        self.__sr.write(LEFT)
        return self.__recv_cmd_packet()         

    def right(self, vv):
        RIGHT[4] = vv
        self.__sr.write(RIGHT)
        return self.__recv_cmd_packet()

    def up(self, ww):
        UP[5] = ww
        self.__sr.write(UP)
        return self.__recv_cmd_packet()

    def down(self, ww):
        DOWN[5] = ww
        self.__sr.write(DOWN)
        return self.__recv_cmd_packet()    

    def __encode_para(self, para):
        paras = [0, 0, 0, 0]
        paras[0] = para >> 12 & 0x0F
        paras[1] = para >> 8 & 0x0F
        paras[2] = para >> 4 & 0x0F
        paras[3] = para & 0x0F
        return paras 
        
    def set_absolute_pos(self, y_para, z_para, vv, ww):
        ABSOLUTE_POS[4] = vv
        ABSOLUTE_POS[5] = ww
        y_paras = self.__encode_para(y_para)
        ABSOLUTE_POS[6:10] = y_paras

        z_paras = self.__encode_para(z_para)
        ABSOLUTE_POS[10:14] = z_paras

        self.__sr.write(ABSOLUTE_POS)
        return self.__recv_cmd_packet()

    def set_zoom(self, z_para):
        z_paras = self.__encode_para(z_para)
        ZOOM_SET[4:8] = z_paras
        self.__sr.write(ZOOM_SET)
        return self.__recv_cmd_packet()

    def stop(self):
        self.__sr.write(STOP)
        return self.__recv_cmd_packet()

    def zoom_tel(self, para):
        tz = 0x20 | para
        ZOOM_TEL[4] = tz
        self.__sr.write(ZOOM_TEL)
        return self.__recv_cmd_packet()

    def zoom_wide(self, para):
        wz = 0x30 | para       
        ZOOM_WIDE[4] = wz
        self.__sr.write(ZOOM_WIDE)
        return self.__recv_cmd_packet()
    # note: it must be called twice
    def zoom_stop(self):
        self.__sr.write(ZOOM_STOP)
        return self.__recv_cmd_packet()

    def preset_clear(self, z):
        MEMORY_RESET[5] = z
        self.__sr.write(MEMORY_RESET)
        return self.__recv_cmd_packet()

    def preset_set(self, z):
        MEMORY_SET[5] = z
        self.__sr.write(MEMORY_SET)
        return self.__recv_cmd_packet()

    def preset_call(self, z):
        MEMORY_CALL[5] = z
        self.__sr.write(MEMORY_CALL)
        return self.__recv_cmd_packet()

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

    def raw(self, value, mode, bas= None):
        self.__sr.write(value)
        if mode == 'ack':
            is_ack = self.__recv_ack_packet()
            return is_ack 
        elif mode == 'complete':
            is_complete = self.__recv_cmd_packet()
            return is_complete
        elif mode == 'info':
            ipacket = self.__get_info(bas)
            return ipacket
        else:
            return False

if __name__ == '__main__':
    import time
    import math

    ptz = Ptz("/dev/cu.usbserial") 

    # test raw
    # test get_pos
    ptz.set_absolute_pos(0, 0, 20, 20)
    time.sleep(2)
    pos = {}
    begin = time.time()
    ptz.get_pos(pos)
    end = time.time()
    if end - begin > 2:
        print 'get_pos timeout'
        sys.exit()
    if pos["x"] == 0 \
        and pos["y"] == 0:
        print 'get_pos is ok'
    else:
        print 'get_pos or set_pos  is err'
        sys.exit()

    # test set_pos
    x = 1000
    y = -300
    ptz.set_absolute_pos(x, y, 24, 24)
    time.sleep(4)
    ptz.get_pos(pos)
    if math.fabs(pos["x"] - x) < 20 \
        and math.fabs(pos["y"] -y) < 10:
        print 'set_pos is ok'
    else:
        print 'set_pos is err'
        sys.exit()

    #test preset
    x = pos["x"]
    y = pos["y"]
    ptz.preset_set(0)
    time.sleep(2)
    ptz.set_absolute_pos(0, 0, 24, 24)
    time.sleep(2)
    ptz.preset_call(0)
    time.sleep(2)
    ptz.get_pos(pos)
    if pos["x"] == x \
        and pos["y"] == y:
        print 'preset_set and preset_call are ok'
    else:
        print 'preset_set or preset_call is err'
        sys.exit()
    ptz.preset_clear(0)
    time.sleep(2)
    ptz.set_absolute_pos(0, 0, 24, 24)
    time.sleep(2)
    ptz.preset_call(0)
    time.sleep(2)
    ptz.get_pos(pos)
    if pos["x"] == 0 \
        and pos["y"] == 0:
        print 'preset_clear is ok'
    else:
        print 'preset_clear is err'
        sys.exit()

    # test stop, left, right, up, down
    ptz.set_absolute_pos(0, 0, 24, 24)
    time.sleep(2)
    ptz.left(10)
    time.sleep(2)
    ptz.stop()
    ptz.get_pos(pos);
    x = pos['x']
    time.sleep(2)
    ptz.get_pos(pos)
    if x == pos['x']:
        print 'stop is ok'
    else:
        print 'stop is err'
        sys.exit()

    if x < 0:
        print 'left is ok'
    else:
        print 'left is err'
        sys.exit()

    ptz.right(10)
    time.sleep(5)
    ptz.stop()
    ptz.get_pos(pos);
    if pos['x'] > x:
        print 'right is ok'
    else:
        print 'right is err'
        sys.exit() 

    y = pos['y']
    ptz.up(10)
    time.sleep(2)
    ptz.stop()
    ptz.get_pos(pos)
    if y < pos['y']:
        print 'up is ok'
        y = pos['y']
    else:
        print 'up is err'
        sys.exit()

    ptz.down(10)
    time.sleep(2)
    ptz.stop()
    ptz.get_pos(pos)
    if y > pos['y']:
        print 'down is ok'
    else:
        print 'down is err'
        sys.exit()

    # test zoom
    ptz.set_zoom(0)
    time.sleep(1)
    zoom = {}
    ptz.get_zoom(zoom)
    begin = time.time()
    ptz.get_zoom(zoom)
    end = time.time()
    if zoom['z'] != 0:
        print 'set_zoom or get_zoom is err'
        sys.exit()
    if end-begin > 2:
        print 'set_zoom timeout'
        sys.exit()
    z = 600
    ptz.set_zoom(z)
    time.sleep(2)
    ptz.get_zoom(zoom)
    if zoom['z'] == z:
        print 'set_zoom and get_zoom are ok'
    else:
        print 'set_zoom and get_zoom is err'
        sys.exit()
    ptz.set_zoom(0)
    ptz.zoom_tel(3)
    time.sleep(2)
    ptz.zoom_stop()
    ptz.zoom_stop()
    ptz.get_zoom(zoom)
    z = zoom['z']
    if z > 0:
        print 'zoom_tel is ok'
    else:
        print 'zoom_tel is err'
        sys.exit()
    ptz.get_zoom(zoom)
    if zoom['z'] == z:
        print 'zoom_stop is ok'
    else:
        print 'zoom_stop is err'
        sys.exit()
    ptz.zoom_wide(3)
    time.sleep(3)
    ptz.zoom_stop()
    ptz.zoom_stop()
    ptz.get_zoom(zoom)
    if zoom['z'] < z:
        print 'zoom_wide is ok'
    else:
        print 'zoom_wide is err'
        sys.exit()

    print '********************'
    print '*                  *' 
    print '*    ptz is ok!    *'
    print '*                  *'
    print '********************'

    
