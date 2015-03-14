# coding: utf-8

import sys, socket, select
import re
sys.path.append('../')
from common.uty_log import log

def TurnStr(name, direction, speed):
    return 'PtzCmd=Turn&Who=%s&Direction=%s&Speed=%s'%(name,direction,speed)

def PresetStr(cmd, name, ids):
    return 'PtzCmd=%s&Who=%s%ID=%s'%(cmd, name, ids) 

def ZoomStr(cmd, name, speed):
    return 'PtzCmd=%s&Who=%s&speed=%s'%(cmd, name, speed)

def toArmStr(name, cmd, params=None):
    if cmd == 'left':
        speed = '1'
        if 'speed' in params:
            speed = params['speed'][0]
        
        return TurnStr(name, 'left', speed)
        
    elif cmd == 'right':
        speed = '1'
        if 'speed' in params:
            speed = params['speed'][0]

        return TurnStr(name, 'right', speed)

    elif cmd == 'up':
        speed = '1'
        if 'speed' in params:
            speed = params['speed'][0]

        return TurnStr(name, 'up', speed)

    elif cmd == 'down':
        speed = '1'
        if 'speed' in params:
            speed = params['speed'][0]

        return TurnStr(name, 'down', speed)
    
    elif cmd == 'stop':
        return 'PtzCmd=StopTurn&Who=%s'%(name)

    elif cmd == 'set_pos':
        sx = '1'
        sy = '1'
        x = str(hex(int(params['x'][0])))
        y = str(hex(int(params['y'][0])))

        if 'sx' in params:
            sx = params['sx'][0]
        if 'sy' in params:
            sy = params['sy'][0]
        return 'PtzCmd=TurnToPos&Who=%s&X=0x%s&Y=0x%s&SX=%s&SY=%s'%(name, x, y, sx, sy)
        
    elif cmd == 'preset_save':
        return PresetStr('PresetSave', name, params['id'][0])    

    elif cmd == 'preset_call':
        return PresetStr('PresetCall', name, params['id'][0])

    elif cmd == 'preset_clear':
        return PresetStr('PresetDel', name, params['id'][0])

    elif cmd == 'zoom_tele':
        speed = '1'
        if 'speed' in params:
            speed = params['speed'][0]
        
        return ZoomStr('ZoomTele', name, speed)

    elif cmd == 'zoom_wide':
        speed = '1'
        if 'speed' in params:
            speed = params['speed'][0]
        return ZoomStr('ZoomWide', name, speed)

    elif cmd == 'zoom_stop':
        return ZoomStr('ZoomStop', name)
    
    else:
        return None


def recvt(s, timeout = 1.0):
    ''' s 接收数据，超时 '''
    r,w,e = select.select([s.fileno()], [], [], timeout)
    if len(r) > 0:
        return s.recv(1024)
    return None

def SendThenRecv(HOST, PORT, arm_command):
    # FIXME: 我感觉应该这样写才能支持连接超时:
    log('ArmPtz.py: ip = %s, port = %s'%(HOST,PORT), 'ptz')
    log('ArmPtz.py: send command = %s'%(arm_command), 'ptz')
    if arm_command == None:
        return {'result':'error', 'info': 'do not support this command'}

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
    try:
        s.settimeout(2)
        s.connect((HOST, PORT))
        s.settimeout(None)
    except Exception as e:
        print e
        log('in ArmPtz.py, connect error:', 'ptz', 1)
        return {'result':'error', 'info':'not connect proxied hos'}
    s.sendall(arm_command) 
    try:
        s.settimeout(2)
        data = s.recv(1024)
        s.settimeout(None)
    except Exception as e:
        s.close()
        print e
        log('in ArmPtz.py, recv error:', 'ptz', 1)
        return {'result':'error', 'info': 'recv timeout or other reasons'}

    s.close()
    print 'recv data'
    print data
    log('ArmPtz.py: recv data %s'%(data), 'ptz')
    if 'ok' in data:
        return {'result':'ok', 'info':''}
    elif 'unsupported' in data:
        return {'result':'error', 'info':'do not support this command'}
    else:
        ret = data.split(',')
        result = ret[0].split(':')[1]
        info = ret[1].split(':')[1]
        return {'result': result, 'info': info} 
