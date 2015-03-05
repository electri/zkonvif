# coding: utf-8
import os
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
		conf = getconf_mulcast()
		c = json.loads(conf)


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
		print sys.path

	def download_file(self, remote_file_url = "",  local_file_name = ""):
		file_version = urlopen(remote_file_url)
		data = file_version.read()
		with open(local_file_name, "wb") as local_zip:
			local_zip.write(data)



	def loadfile(self, file_name, config):
		with open(file_name, "r") as f:
			for line in f.readlines():
				line = line.strip("\n")
				print line
				arr = line.split("=",2)
				if len(arr) == 2:
					config[arr[0].strip()] = arr[1].strip()
		print config

	def savefile(self, file_name, config):
		with open(file_name, "wb") as f:
			for key in config:
				f.write(key + '=' + config[key] + '\n')


	def extract_zip(self, zip_file_name, folder = ""):
		f = zipfile.ZipFile(zip_file_name, "r")
		for file in f.namelist():
			f.extract(file, folder)

	def checkVersionProcess(self):
		self.download_file(self.version_url, self.version_file_name)

		self.loadfile(self.version_file_name, self.remote_version_config)

		#如果py文件有更新，先更新py文件，退出后再次运行
		if self.local_version_config["py_version"] != self.remote_version_config["py_version"]:
			self.download_file(self.py_url, self.py_file_name)
			self.local_version_config["py_version"] = self.remote_version_config["py_version"]
			#self.savefile(self.version_local_file_name, self.local_version_config)


		if self.local_version_config["zip_version"] != self.remote_version_config["zip_version"]:
			self.download_file(self.zip_url, self.zip_file_name)
			self.extract_zip(self.zip_file_name, "./test")
			self.local_version_config["zip_version"] = self.remote_version_config["zip_version"]

		self.savefile(self.version_local_file_name, self.local_version_config)

if __name__ == "__main__":
	check = CheckVersion()

	check.checkVersionProcess()
	abspath = os.path.abspath(__file__)
	print abspath

