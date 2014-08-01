# coding: utf-8

from ctypes import *
import platform, os



_ptz_so = 'libzkptz.so.0.0.0'

plat = platform.uname()[0]

if plat == 'Darwin':
	_ptz_so = './osx/libzkptz.dylib'
elif plat == 'Windows':
	_ptz_so = r'win32\zkptz.dll'
elif plat == 'Linux':
	if platform.uname()[4].find('arm') >= 0:
		_ptz_so = './arm/libzkptz.so.0.0.0'
	else:
		_ptz_so = './linux/libzkptz.so.0.0.0'
elif plat.find('CYGWIN') >= 0:
	_ptz_so = './cygwin64/zkptz.dll'
else:
	_ptz_so = None

print 'using PTZ mod:', _ptz_so



class PtzWrap(object):
	''' 封装 libzkptz.so 的调用
	'''
	def __init__(self):
		self.__ptr = self.__load_ptz_module()
		self.__ptz = None


	def open(self, serial, addr):
		''' 打开串口...
		'''
		if self.__ptr['so']:
			self.__ptz = self.__ptr['func_open'](serial, addr)
			return (self.__ptz != None)
		else:
			return False


	def close(self):
		if self.__ptz:
			self.__ptr['func_close'](self.__ptz)
			self.__ptz = None

	
	def call(self, method, params):
		''' 执行 method 命令，使用 params 作为参数 ...
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
		elif method == 'get_pos':
			ret.update(self.get_pos())
		elif method == 'set_pos':
			ret.update(self.set_pos(params))
		elif method == 'get_zoom':
			ret.update(self.get_zoom())
		elif method == 'set_zoom':
			ret.update(self.set_zoom(params))
		else:
			ret.update({'result':'error', 'info':'method NOT supported'})
		return ret


	def stop(self):
		if not self.__ptz:
			return {'result':'error', 'info':'NO ptz'}
		else:
			self.__ptr['func_stop'](self.__ptz)
			return { 'info':'completed' }


	def left(self, params):
		if not self.__ptz:
			return {'result':'error', 'info':'NO ptz'}
		else:
			speed = 1
			if 'speed' in params:
				speed = int(params['speed'][0])
			self.__ptr['func_left'](self.__ptz, speed)
			return { 'info':'completed' }


	def right(self, params):
		if not self.__ptz:
			return {'result':'error', 'info':'NO ptz'}
		else:
			speed = 1
			if 'speed' in params:
				speed = int(params['speed'][0])
			self.__ptr['func_right'](self.__ptz, speed)
			return { 'info':'completed' }


	def up(self, params):
		if not self.__ptz:
			return {'result':'error', 'info':'NO ptz'}
		else:
			speed = 1
			if 'speed' in params:
				speed = int(params['speed'][0])
			self.__ptr['func_up'](self.__ptz, speed)
			return { 'info':'completed' }


	def down(self, params):
		if not self.__ptz:
			return {'result':'error', 'info':'NO ptz'}
		else:
			speed = 1
			if 'speed' in params:
				speed = int(params['speed'][0])
			self.__ptr['func_down'](self.__ptz, speed)
			return { 'info':'completed' }


	def get_pos(self):
		if not self.__ptz:
			return {'result':'error', 'info':'NO ptz'}
		else:
			x = c_int()
			y = c_int()
			if self.__ptr['func_get_pos'](self.__ptz, byref(x), byref(y)) == 0:
				return { 'value': { 'type':'position', 'data': {'x': x.value, 'y': y.value} } }
			else:
				return { 'result':'error', 'info':'get_pos failure' }


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
			self.__ptr['func_set_pos'](self.__ptz, x, y, sx, sy)
			return { 'info':'completed' }


	def get_zoom(self):
		if not self.__ptz:
			return {'result':'error', 'info':'NO ptz'}
		else:
			z = c_int()
			if self.__ptr['func_get_zoom'](self.__ptz, byref(z)) == 0:
				return {'value': { 'type':'position', 'data': {'z':z.value }}}
			else:
				return {'result':'error', 'info':'get_zoom failure' }


	def set_zoom(self, params):
		if not self.__ptz:
			return {'result':'error', 'info':'NO ptz'}
		else:
			z = 0
			if 'z' in params:
				z = int(params['z'][0])
			self.__ptr['func_set_zoom'](self.__ptz, z)
			return { 'info':'completed' }


	def __load_ptz_module(self):
		''' 加载 ptz 模块 '''
		ptz = {}
		global _ptz_so
		if _ptz_so is None:
			_ptz_so = './libzkptz.dylib'
		ptz['so'] = CDLL(_ptz_so)
		print ptz['so']
		ptz['func_open'] = ptz['so'].ptz_open
		ptz['func_open'].restype = c_void_p
		ptz['func_close'] = ptz['so'].ptz_close
		ptz['func_close'].argtypes = [c_void_p]
		ptz['func_get_pos'] = ptz['so'].ptz_get_pos
		ptz['func_get_pos'].argtypes = [c_void_p, POINTER(c_int), POINTER(c_int)]
		ptz['func_set_pos'] = ptz['so'].ptz_set_pos
		ptz['func_set_pos'].argtypes = [c_void_p, c_int, c_int, c_int, c_int]
		ptz['func_left'] = ptz['so'].ptz_left
		ptz['func_left'].argtypes = [c_void_p, c_int]
		ptz['func_right'] = ptz['so'].ptz_right
		ptz['func_right'].argtypes = [c_void_p, c_int]
		ptz['func_up'] = ptz['so'].ptz_up
		ptz['func_up'].argtypes = [c_void_p, c_int]
		ptz['func_down'] = ptz['so'].ptz_down
		ptz['func_down'].argtypes = [c_void_p, c_int]
		ptz['func_stop'] = ptz['so'].ptz_stop
		ptz['func_stop'].argtypes = [c_void_p]
		ptz['func_set_zoom'] = ptz['so'].ptz_set_zoom
		ptz['func_set_zoom'].argtypes = [c_void_p, c_int]
		ptz['func_get_zoom'] = ptz['so'].ptz_get_zoom
		ptz['func_get_zoom'].argtypes = [c_void_p, POINTER(c_int)]
		return ptz


