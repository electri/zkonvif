import socket
import re

def TurnStr(name, direction, speed):
	return 'PtzCmd=Turn&Who=%s&Direction=%s&Speed=%s'%(name,direction,speed)

def PresetStr(cmd, name, ids):
	return 'PtzCmd=%s&Who=%s%ID=%s'%(cmd, name, ids) 

def ZoomStr(cmd, name, speed):
	return 'ptzCmd=%s&Who=%s&speed=%s'%(cmd, name, speed)

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
		
		return ZoomStr('Zoom_tele', name, speed)

	elif cmd == 'zoom_wide':
		speed = '1'
		if 'speed' in params:
			speed = params['speed'][0]
		return ZoomStr('Zoom_wide', name, speed)

	elif cmd == 'zoom_stop':
		return ZoomStr('ZoomStop', name)
	
	else:
		return None

def SendThenRecv(HOST, PORT, arm_command):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	
    try:
	    s.connect((HOST, PORT))
    except Exception as e:
        print e
        return {'result':'error', 'info':'not connect proxied hos'}
	s.sendall(arm_command)
	data = s.recv(1024)
    ret = data.split(',')
    result = ret[0].split(':')[1]
    info = ret[1].split(':')[1]
	s.close()

	return {'result':result, 'info':info} 
