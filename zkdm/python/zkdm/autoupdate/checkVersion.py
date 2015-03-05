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
		#日志格式
		logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='update.log',
                filemode='w')

		#################################################################################################
		#定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
		console = logging.StreamHandler()
		console.setLevel(logging.DEBUG)
		formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
		console.setFormatter(formatter)
		logging.getLogger('').addHandler(console)
		#################################################################################################

		#获得更新url
		conf = getconf_mulcast()
		c = json.loads(conf)
		logging.debug(c)

		self.py_url = c['AutoUpdate']['version']
		self.version_url = c['AutoUpdate']['version']
		self.zip_url = c['AutoUpdate']['package']

		self.py_file_name = "checkVersion.py"
		self.py_url = self.py_url.rstrip("version")  + self.py_file_name



		self.version_file_name = "version"
		self.version_local_file_name = "local"
		self.zip_file_name = "text.zip"
		self.local_version_config = {}
		self.remote_version_config = {}
		self.loadfile(self.version_local_file_name, self.local_version_config)
		logging.debug("开始下载文件%s"%self.zip_file_name)


	def download_file(self, remote_file_url = "",  local_file_name = ""):
		try:

			file_version = urlopen(remote_file_url)
			data = file_version.read()
		except Exception, ex:
			logging.debug(ex)

		with open(local_file_name, "wb") as local_zip:
			local_zip.write(data)



	def loadfile(self, file_name, config):
		with open(file_name, "r") as f:
			for line in f.readlines():
				line = line.strip("\n")
				arr = line.split("=",2)
				if len(arr) == 2:
					config[arr[0].strip()] = arr[1].strip()

	def savefile(self, file_name, config):
		with open(file_name, "wb") as f:
			for key in config:
				f.write(key + '=' + config[key] + '\n')


	def extract_zip(self, zip_file_name, folder = ""):
		try:
			f = zipfile.ZipFile(zip_file_name, "r")
			for file in f.namelist():
				f.extract(file, folder)
		except Exception,ex:
			logging.debug(ex)

	def checkVersionProcess(self):
		logging.debug("下载version文件")
		self.download_file(self.version_url, self.version_file_name)

		logging.debug("加载version文件，进行比对")
		self.loadfile(self.version_file_name, self.remote_version_config)

		logging.debug("检查py文件是否有更新")
		if self.local_version_config["py_version"] != self.remote_version_config["py_version"]:
			logging.debug("更新py文件")
			self.download_file(self.py_url, self.py_file_name)
			self.local_version_config["py_version"] = self.remote_version_config["py_version"]
			#self.savefile(self.version_local_file_name, self.local_version_config)

		logging.debug("检查zip文件是否有更新")
		if self.local_version_config["zip_version"] != self.remote_version_config["zip_version"]:
			logging.debug("更新zip文件")
			self.download_file(self.zip_url, self.zip_file_name)
			self.extract_zip(self.zip_file_name, "./test")
			self.local_version_config["zip_version"] = self.remote_version_config["zip_version"]

		self.savefile(self.version_local_file_name, self.local_version_config)

if __name__ == "__main__":
	check = CheckVersion()

	check.checkVersionProcess()
	#abspath = os.path.abspath(__file__)
	#print abspath

