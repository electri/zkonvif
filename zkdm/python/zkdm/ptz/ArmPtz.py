# coding: utf-8

import sys, socket, select
import re


def TurnStr(name, direction, speed):
    return 'PtzCmd=Turn&Who=%s&Direction=%s&Speed=%s'%(name,direction,speed)

def PresetStr(cmd, name, ids):
    return 'PtzCmd=%s&Who=%s&ID=%s'%(cmd, name, ids) 

def ZoomStr(cmd, name, speed):
    return 'PtzCmd=%s&Who=%s&speed=%s'%(cmd, name, speed)

def ZoomStrWithoutSpeed(cmd, name):
    return 'PtzCmd=%s&Who=%s'%(cmd, name)

def toArmStr(name, cmd, params=None):
    if cmd == 'left':
        speed = '1'
        if 'speed' in params:
            speed = params['speed'][0]
        return TurnStr(name, 'left', speed)

    elif cmd == 'get_pos':
        return 'PtzCmd=GetPos&Who={}'.format(name)

    elif cmd == 'get_zoom':
        return 'PtzCmd=GetZoom&Who={}'.format(name)

    elif cmd == 'set_zoom':
        zoom = 0
        if 'z' in params:
            z = int(params['z'][0])
        return 'PtzCmd=SetZoom&Who={}&Zoom={}'.format(name, zoom);
        
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
        sx = 30
        sy = 30
        x = int(params['x'][0])
        y = int(params['y'][0])

        if 'sx' in params:
            sx = int(params['sx'][0])
        if 'sy' in params:
            sy = int(params['sy'][0])
        return 'PtzCmd=TurnToPos&Who=%s&X=%d&Y=%d&SX=%d&SY=%d'%(name, x, y, sx, sy)
        
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
        return ZoomStrWithoutSpeed('ZoomStop', name)
    
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
    if arm_command == None:
        return (False, 'command is None???')

    print 'req:', arm_command

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
    try:
        s.settimeout(2)
        s.connect((HOST, PORT))
        s.settimeout(None)
    except Exception as e:
        print e
        return (False, 'not connect proxied host %s:%d' % (HOST, PORT))

    s.sendall(arm_command) 

    try:
        s.settimeout(2)
        data = s.recv(1024)
        s.settimeout(None)
    except Exception as e:
        s.close()
        print e
        return (False, 'recv timeout or other reasons')

    s.close()

    print 'recv data', data

    res = data.strip()
    res = data.strip('###')
    if 'unsupported' in data:
        return (False, 'unsipported')
    elif 'error' in data:
        return (False, data)
    else:
        return (True, data)


def func_without_res(ip, port, who, method, args):
    cmd_str = toArmStr(who, method, args)
    ret, reason = SendThenRecv(ip, port, cmd_str)
    if ret:
        return { 'result':'ok', 'info': reason }
    else:
        return { 'result': 'error', 'info': reason }

def func_get_pos(ip, port, who, method, args):
    cmd_str = toArmStr(who, method, args)
    ret, reason = SendThenRecv(ip, port, cmd_str)
    if ret:
        if 'X=' in reason and 'Y=' in reason:
            x_and_y = reason.split('&')
            x_str = x_and_y[0].split('=')
            x = int(x_str[1])
            y_str = x_and_y[1].split('=')
            y = int(y_str[1])

            return {'result':'ok', 'info':'', \
                'value': { 'type':'position', \
                    'data': {'x': x, 'y': y } } }
        else:
            return { 'result':'error', 'info': 'd3100 return invalid format' }

    else:
        return {'result': 'error', 'info': reason }


def func_get_zoom(ip, port, who, method, args):
    cmd_str = toArmStr(who, method, args)
    ret, reason = SendThenRecv(ip, port, cmd_str)
    if ret:
        if 'Zoom' in reason:
            z_str = reason.split('=')
            z = int(z_str[1])

            return {'result':'ok', 'info':'', \
                'value': { 'data': { 'z': z } } }
        else:
            return { 'result':'error', 'info': 'd3100 return invalid format' }
           
    else:
        return {'result': 'error', 'info': reason }


_tables = {
    'left': func_without_res,
    'right': func_without_res,
    'up': func_without_res,
    'down': func_without_res,
    'stop': func_without_res,
    'set_pos': func_without_res,
    'set_zoom': func_without_res,
    'preset_call': func_without_res,
    'preset_save': func_without_res,
    'preset_clear': func_without_res,
    'zoom_tele': func_without_res,
    'zoom_wide': func_without_res,
    'zoom_stop': func_without_res,

    'get_pos': func_get_pos,
    'get_zoom': func_get_zoom,
}


def call(ip, port, who, method, args):
    if method in _tables:
        return _tables[method](ip, port, who, method, args)
    else:
        return { 'result': 'error', 'info': 'NOT supported method' }


if __name__ == '__main__':
    ip = '192.168.12.238'
    port = 1240

    print call(ip, port, 'teacher', 'left', { 'speed':[3] })
    print call(ip, port, 'teacher', 'stop', None)

    print call(ip, port, 'teacher', 'set_pos', { 'x':[400], 'y':[400] })
    print call(ip, port, 'teacher', 'get_pos', None)
    print call(ip, port, 'teacher', 'get_zoom', None)

