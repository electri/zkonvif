# coding: utf-8

import platform, os
from ctypes import *

_uname = platform.uname()
_soname = 'linux/libzkutils.so'

if _uname[0] == 'Darwin':
	_soname = 'osx/libzkutils.dylib'
elif _uname[0] == 'Linux':
	# TODO: 应该检测 32/64 ...
	if _uname[4].find('arm') == 0:
		_soname = 'arm/libzkutils.so'
	else:
		_soname = 'linux/libzkutils.so'
elif _uname[0] == 'Windows':
	if _uname[4] == 'AMD64':
        print 'AMD64'
		_soname = 'win32/zkutils.dll'
	else:
		_soname = 'win32/zkutils.dll'
        print 'windows other'
elif _uname[0].find('CYGWIN') >= 0:
	if _uname[4] == 'x86_64':
		_soname = './win64/zkutils.dll'
	else:
		_soname = 'win32/zkutils.dll'
else:
	_soname = None


if _soname == None:
	print 'un-supported platform !!!!'
else:
	print 'using:', _soname



class zkutils:
	''' 封装 libzkutil.so '''
	def __init__(self):
		curr_path = os.getcwd()
		t_path = os.path.dirname(os.path.abspath(__file__))
		os.chdir(t_path)
		self.__so = CDLL(_soname)
		os.chdir(curr_path)
		self.__get_myip = self.__so.util_get_myip
		self.__get_myip.restype = c_char_p

		self.__get_mymac = self.__so.util_get_mymac
		self.__get_mymac.restype = c_char_p

		self.__get_myip_real = self.__so.util_get_myip_real
		self.__get_myip_real.restype = c_char_p

		self.__get_nic_name = self.__so.util_get_nic_name
		self.__get_nic_name.restype = c_char_p



	def myip(self):
		return self.__get_myip()


	def myip_real(self):
		return self.__get_myip_real()


	def mymac(self):
		return self.__get_mymac()


	def nicname(self):
		return self.__get_nic_name()


if __name__ == '__main__':
	u = zkutils()
	print u.myip()
	print u.myip_real()
	print u.mymac()
	print u.nicname()

