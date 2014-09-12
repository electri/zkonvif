# coding: utf-8


import socket

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
		s=socket.socket()
		host=self.get_ip()
		port=1230
		s.connect((host,port))
		s.send(command)
		message=""
		#发送命令后录像程序没有返回消息，先注销
		#message=s.recv(512)
		s.close()
		return message
	

	def start(self):
		self.send_command('RecordCmd=StartRecord')

	def pause(self):
		self.send_commad('RecordCmd=PauseRecord')

	def stop(self):
		self.send_command('RecordCmd=StopRecord')
	
	def resume(self):
		self.send_command('RecordCmd=ResumeRecord')


def main():
	ss=RecordingCommand()
	ss.start()


if __name__ == "__main__":
	main()