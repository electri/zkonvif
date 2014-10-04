# coding: utf-8

from ctypes import *
import platform, os



_ptz_so = 'libzkptz.so.0.0.0'

plat = platform.uname()[0]

if plat == 'Darwin':
	_ptz_so = './osx/libzkptz.dylib'
elif plat == 'Windows':
	_ptz_so = r'win32/zkptz.dll'
elif plat == 'Linux':
	if platform.uname()[4].find('arm') >= 0:
		_ptz_so = './arm/libzkptz.so.0.0.0'
	else:
		_ptz_so = './linux/libzkptz.so.0.0.0'
elif plat.find('CYGWIN') >= 0:
	_ptz_so = './cygwin64/zkptz.dll'
else:
	_ptz_so = None


#raw_input("press ")


class PtzWrap(object):
	''' 封装 libzkptz.so 的调用
	'''
	def __init__(self):
		cpath = os.getcwd()
		tpath = os.path.dirname(os.path.abspath(__file__))
		os.chdir(tpath)
		self.__ptr = self.__load_ptz_module()
		self.__ptz = None
		os.chdir(cpath)


	def open(self, serial, addr):
		''' 已经废弃，应该使用 open_with_config()
		'''
		if self.__ptr['so']:
			self.__ptz = self.__ptr['func_open'](serial, addr)
			return (self.__ptz != None)
		else:
			return False


	def open_with_config(self, cfg_filename):
		''' 优先使用该方法，支持 mouse_track, ptz_ext_xxx '''
		if self.__ptr['so']:
			self.__ptz = self.__ptr['func_open2'](cfg_filename)
			return (self.__ptz is not None)
		else:
			return False


	def close(self):
		if self.__ptz:
			self.__ptr['func_close'](self.__ptz)
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
		elif method == 'get_zoom':
			ret.update(self.get_zoom())
		elif method == 'set_zoom':
			ret.update(self.set_zoom(params))
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

	def preset_save(self, params):
		if not self.__ptz:
			return {'result':'error', 'info':'NO ptz'}
		else:
			if 'id' in params:
				id = int(params['id'][0])
				self.__ptr['func_preset_save'](self.__ptz, id)
				return {'info':'completed'}
			else:
				return {'result':'error', 'info':'NO liuwenen id'}
		
	def preset_call(self, params):
		if not self.__ptz:
			return {'result':'error', 'info':'NO ptz'}
		else:
			if 'id' in params:
				id = int(params['id'][0])
				self.__ptr['func_preset_call'](self.__ptz, id)
				return {'info':'completed'}
			else:
				return {'result':'error', 'info':'NO id'}


	def preset_clear(self, params):
		if not self.__ptz:
			return {'result':'error', 'info':'NO ptz'}
		else:
			if 'id' in params:
				id = int(params['id'][0])
				self.__ptr['func_preset_clear'](self.__ptz, id)
				return {'info':'completed'}
			else:
				return {'result':'error', 'info':'NO id'}			


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

	def get_pos_zoom(self):
			if not self.__ptz:
				return {'result':'error', 'info':'No PTZ'}
			else:
				x = c_int()
				y = c_int()
				z = c_int()
				is_pos = self.__ptr['func_get_pos'](self.__ptz, byref(x), byref(y))
				is_zoom = self.__ptr['func_get_zoom'](self.__ptz, byref(z))
				
				if (is_pos==0) and (is_zoom==0):
					return {'value': { 'type':'position', 'data': {'x': x.value, 'y': y.value, 'z': z.value} } }
				else:
					return {'result':'error', 'info':'No PTZ'}
			
	def ext_get_scales(self):
		if not self.__ptz:
			return { 'result':'error', 'info':'NO ptz' }
		else:
			return { 'value': { 'type':'double', 'data': self.__ptr['func_ext_get_scales'](self.__ptz, -1) } }


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

	def mouse_trace(self, params):
			if not self.__ptz:
				return {'return':'error', 'info':'NO ptz'}
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
				self.__ptr['func_mouse_trace'](self.__ptz, x, y, sx, sy)
				return {'info':'completed'}

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


	def zoom_wide(self, params):
		if not self.__ptz:
			return {'result':'error', 'info':'NO ptz'}
		else:
			speed = 1
			if 'speed' in params:
				speed = int(params['speed'][0])
			self.__ptr['func_zoom_wide'](self.__ptz, speed)
			return {'info':'completed'}


	def zoom_tele(self, params):
		if not self.__ptr:
			return {'result':'error', 'info':'NO ptz'}
		else:
			speed = 1
			if 'speed' in params:
				s = int(params['speed'][0])
			self.__ptr['func_zoom_tele'](self.__ptz, speed)
			return {'info':'complete'}


	def zoom_stop(self):
		if not self.__ptr:
			return {'result':'error', 'info':'NO ptz'}
		else:
			self.__ptr['func_zoom_stop'](self.__ptz)
			return {'info':'complete'}


	def __load_ptz_module(self):
		''' 加载 ptz 模块 '''
		ptz = {}
		print 'en ........ to load:', _ptz_so
		ptz['so'] = CDLL(_ptz_so)

		ptz['func_open'] = ptz['so'].ptz_open
		ptz['func_open'].restype = c_void_p

		ptz['func_open2'] = ptz['so'].ptz_open_with_config
		ptz['func_open2'].argtypes = [c_char_p]
		ptz['func_open2'].restype = c_void_p

		ptz['func_close'] = ptz['so'].ptz_close
		ptz['func_close'].argtypes = [c_void_p]

		ptz['func_get_pos'] = ptz['so'].ptz_get_pos
		ptz['func_get_pos'].argtypes = [c_void_p, POINTER(c_int), POINTER(c_int)]

		ptz['func_set_pos'] = ptz['so'].ptz_set_pos
		ptz['func_set_pos'].argtypes = [c_void_p, c_int, c_int, c_int, c_int]

		ptz['func_preset_save'] = ptz['so'].ptz_preset_save
		ptz['func_preset_save'].argtypes = [c_void_p, c_int]

		ptz['func_preset_call'] = ptz['so'].ptz_preset_call
		ptz['func_preset_call'].argtypes = [c_void_p, c_int]

		ptz['func_preset_clear'] = ptz['so'].ptz_preset_clear
		ptz['func_preset_clear'].argtypes = [c_void_p, c_int]

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

		ptz['func_zoom_wide'] = ptz['so'].ptz_zoom_wide
		ptz['func_zoom_wide'].argtypes = [c_void_p, c_int]

		ptz['func_zoom_tele'] = ptz['so'].ptz_zoom_tele
		ptz['func_zoom_tele'].argtypes = [c_void_p, c_int]

		ptz['func_zoom_stop'] = ptz['so'].ptz_zoom_stop
		ptz['func_zoom_stop'].argtypes = [c_void_p]

#		ptz['func_mouse_trace'] = ptz['so'].ptz_mouse_trace
#		ptz['func_mouse_trace'].argtypes = [c_void_p, c_int, c_int, c_int, c_int] 

		ptz['func_ext_get_scales'] = ptz['so'].ptz_ext_get_scals
		ptz['func_ext_get_scales'].argtypes = [c_void_p, c_int]
		ptz['func_ext_get_scales'].restype = c_double

		return ptz




