import config_utils as cu
from socket import *

def get_value(fname, key):
	cfg = cu.ConfigUtils(fname)
	kvs = cfg.read_cfg()
	if kvs.key(key+'=') is not True:
		return ''
	return kvs[key]

def send_udp_data(data, remote_id, remote_port = 8642):
	try:
		port = get_value('global.trace.policy.config', 'udp_listen_port')
	except:
		pass
	else:
		if port != '':
			remote_port = int(port)
	address = (remote_id, remote_port)
	client_socket = socket(AF_INET, SOCK_DGRAM)
	client_socket.sendto(data, address)

if __name__ == '__main__':
	send_udp_data('\x09\x01', '172.16.1.113')
