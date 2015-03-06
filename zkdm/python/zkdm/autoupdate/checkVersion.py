# coding: utf-8
import os
import logging
import sys
from urllib2 import urlopen, URLError, HTTPError
import zipfile
from conf_mc import *

#self.local_py_version = "1.0"
#self.remote_py_version = "1.0"
#self.local_zip_version = "1.0"
#self.removte_zip_version = "1.0"
class CheckVersion:
	def __init__(self):
		#日志大于5M，删除
		if os.path.getsize("update.log") > 5000000:
			os.remove("update.log")
		#日志格式
		logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='update.log',
                filemode='a')

		#################################################################################################
		#定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
		console = logging.StreamHandler()
		console.setLevel(logging.DEBUG)
		formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
		console.setFormatter(formatter)
		logging.getLogger('').addHandler(console)
		#################################################################################################
		logging.debug("#################################################################################################")
		#获得更新url
		conf = getconf_mulcast()
		c = json.loads(conf)
		logging.debug(c)

		#self.py_url = c['AutoUpdate']['version']
		self.version_url = c['AutoUpdate']['version']
		self.zip_url = c['AutoUpdate']['package']

		self.py_file_name = "checkVersion.py"
		#self.py_url = self.py_url.rstrip("version")  + self.py_file_name



		self.version_file_name = "version"
		self.version_local_file_name = "local"
		self.zip_file_name = "text.zip"
		self.local_version_config = {}
		self.remote_version_config = {}




	def download_file(self, remote_file_url = "",  local_file_name = ""):
		try:
			file_version = urlopen(remote_file_url)
			data = file_version.read()
			print len(data)
			with open(local_file_name, "wb") as local_zip:
				local_zip.write(data)
			return True

		except Exception, ex:
			logging.debug(ex)
			return False





	def loadfile(self, file_name, config):
		try:
			f = open(file_name, "r")
			for line in f.readlines():
				line = line.strip("\n")
				arr = line.split("=",2)
				if len(arr) == 2:
					config[arr[0].strip()] = arr[1].strip()
			return True
		except Exception,ex:
			logging.debug(ex)
			return False

	def savefile(self, file_name, config):
		with open(file_name, "wb") as f:
			for key in config:
				f.write(key + '=' + config[key] + '\n')

	#py文件最后解压，version和local不解压
	def extract_zip(self, zip_file_name, folder = ""):
		try:
			lastfile = None
			f = zipfile.ZipFile(zip_file_name, "r")
			for file in f.namelist():
				if file.find(self.py_file_name) != -1:
					lastfile = file
					continue
				if file.find("autoupdate/version")!=-1 or file.find("autoupdate/local")!= -1 or file.find("autoupdate/update.log") != -1:
					continue
				f.extract(file, folder)
			if lastfile != None:
				f.extract(lastfile, folder)
			f.close()
			return True
		except Exception,ex:
			logging.debug(ex)
			return False

	def checkVersionProcess(self):
		self.loadfile(self.version_local_file_name, self.local_version_config)

		bZipModify = False
		logging.debug("下载version文件")
		if self.download_file(self.version_url, self.version_file_name) == False:
			return False

		logging.debug("加载version文件，进行比对")
		if self.loadfile(self.version_file_name, self.remote_version_config) == False:
			return False

		# logging.debug("检查py文件是否有更新")
		# if self.local_version_config.get("py_version") != self.remote_version_config.get("py_version"):
		# 	logging.debug("更新py文件")
		# 	self.download_file(self.py_url, self.py_file_name)
		# 	self.local_version_config["py_version"] = self.remote_version_config.get("py_version")
		#
		# 	self.savefile(self.version_local_file_name, self.local_version_config)
		#
		# 	return False

		logging.debug("检查zip文件是否有更新")
		if self.local_version_config.get("zip_version") != self.remote_version_config.get("zip_version"):
			logging.debug("更新zip文件")
			if self.download_file(self.zip_url, self.zip_file_name) == False:
				return False

			logging.debug("解压zip文件")
			if self.extract_zip(self.zip_file_name, "../") == False:
				return False
			self.local_version_config["zip_version"] = self.remote_version_config.get("zip_version")
			bZipModify = True


		self.savefile(self.version_local_file_name, self.local_version_config)
		return bZipModify

if __name__ == "__main__":
	check = CheckVersion()

	check.checkVersionProcess()
	#abspath = os.path.abspath(__file__)
	#print abspath

