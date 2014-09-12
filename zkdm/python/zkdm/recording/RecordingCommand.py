# coding: utf-8

import socket
import getopt, sys

class RecordingCommand():
	"""
	"""
	def __init__(self):
		pass
	

	def get_ip(self):
		my_name = socket.getfqdn(socket.gethostname())
		my_ip=socket.gethostbyname(my_name)
		return my_ip


	#录像程序的监听端口号为固定的1230
	def send_command(self,command):
		rc={}
		rc['result']='ok'
		rc['info']=''
		try:
			s=socket.socket()
			host=self.get_ip()
			port=1230
			s.connect((host,port))
			s.send(command)
			#message=""
			#发送命令后录像程序没有返回消息，先注销
			#message=s.recv(512)
			s.close()
		except Exception as err:
			rc['result']='error'
			rc['info']=str(err)

		return rc

	def start(self):
		rc=self.send_command('RecordCmd=StartRecord')
		return rc

	def pause(self):
		rc=self.send_command('RecordCmd=PauseRecord')
		return  rc

	def stop(self):
		rc=self.send_command('RecordCmd=StopRecord')
		return rc
	
	def resume(self):
		rc=self.send_command('RecordCmd=ResumeRecord')
		return rc


def main():
	ss=RecordingCommand()
	ss.start()


if __name__ == "__main__":
	main()