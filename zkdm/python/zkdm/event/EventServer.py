# coding: utf-8
# 里面的“修饰符”用法，完全一头雾水啊 ...

from tornado.web import *
from tornado.ioloop import IOLoop
from tornado.gen import  *
import sys, time
import threading, Queue
from socket import *
from functools import wraps
import json

sys.path.append('../')

from common.KVConfig import KVConfig


class LazyQueue(object):
	''' 这个 fifo，只进不出，但当超过 maxitems 时，扔掉头 '''
	def __init__(self, maxitem):
		self.__maxitem = maxitem
		if self.__maxitem < 1:
			self.__maxitem = 1
		self.__fifo = []
		self.__mutex = threading.RLock()


	def push(self, item):
		self.__mutex.acquire()
		while len(self.__fifo) >= self.__maxitem:
			del self.__fifo[0]
		self.__fifo.append(item)
		self.__mutex.release()


	def all(self):
		items = []
		self.__mutex.acquire()
		for x in self.__fifo:
			items.append(x)
		self.__mutex.release()
		return items
	

# 保存启动后收到的所有本地消息 ...
_lazyMessages = LazyQueue(1000)
_all_pps = None


class Message:
	''' 通知消息 , 模拟成一个 dict ??
	'''
	def __init__(self, catalog, sid, code, info = ''):
		self.__catalog = catalog
		self.__sid = sid
		self.__code = code
		self.__info = info
		self.__stamp = time.time()


	def catalog(self):
		return self.__catalog


	def sid(self):
		return self.__sid


	def code(self):
		return self.__code


	def info(self):
		return self.__info


	def stamp(self):
		return self.__stamp
	

	def __repr__(self):
		return str(self.dict())


	def dict(self):
		return { 
			'catalog': self.__catalog,
			'sid': self.__sid,
			'code': self.__code,
			'info': self.__info,
			'stamp': self.__stamp,
		}



class LocalUdpRecver(threading.Thread):
	''' 接收本地 udp 消息 ...
		使用独立的工作线程 ...
	'''
	def __init__(self):
		threading.Thread.__init__(self)
		self.daemon = True	# 为了无条件结束 ...


	def run(self):
		sock = socket(AF_INET, SOCK_DGRAM)
		sock.bind(("127.0.0.1", 10001))
		while True:
			data, addr = sock.recvfrom(4096)
			msg = self.__decode(data)
			if msg:
				if msg.catalog() == '!exit':
					break
				_lazyMessages.push(msg)
				if _all_pps:
					_all_pps.push(msg)
		sock.close()
	
	
	def __decode(self, data):
		''' 解析收到的数据，如果是 Message，则加入全局队列中 ...
			data的格式：
			   使用\n分割：
			   		<catalog>\n<sid>\n<code>\n<info>\n
		'''
		ss = data.split('\n', 3)
		if len(ss) == 4:
			code = 0
			try:
				code = int(ss[2])
			except:
				code = 0
			return Message(ss[0], ss[1], code, ss[3])
		else:
			return None


class PullPoint:
	''' 对应一个订阅点 '''
	def __init__(self, pid):
		self.__pid = pid
		self.__queue = Queue.Queue()
		self.__event = threading.Event()


	def pid(self):
		return self.__pid


	def __str__(self):
		return 'pp: #' + str(self.__pid)


	def __repr__(self):
		return 'pp: ##' + str(self.__pid)

		
	def __get_all_pending(self):
		msgs = []
		while True:
			try:
				msgs.append(self.__queue.get(False))
			except:
				break
		return msgs


	def put_message(self, msgs):
		''' 保存收到的消息 '''
		for msg in msgs:
			self.__queue.put(msg)
		self.__event.set()


	def get_message(self):
		''' 返回消息，如果无消息，最多等待 10秒 '''
		if self.__queue.empty():
			if self.__event.wait(10.0):
				self.__event.clear()
				return self.__get_all_pending()
			else:
				return [] # 超时 ..
		else:
		  	return self.__get_all_pending()



class PullPoints:
	''' 管理多个 PullPoint '''
	def __init__(self):
		self.__items = []
		self.__lock = threading.RLock()
		self.__next_pid = 1


	def lock(self):
		self.__lock.acquire()
		return self.__items


	def unlock(self):
		self.__lock.release()

		
	def create(self):
		''' 创建一个通知点，并加入 __items '''
		pp = PullPoint(self.__next_pid)
		items = self.lock()
		self.__next_pid = self.__next_pid+1
		items.append(pp)
		self.unlock()
		pp.put_message(_lazyMessages.all()) # 所有缓冲的消息 ...
		return pp


	def destroy(self, pp):
		''' 删除 pp '''
		items = self.lock()
		items.remove(pp)
		self.unlock()


	def get_pp(self, pid):
		items = self.lock()
		pp = None
		for x in items:
			if x.pid() == pid:
				pp = x
				break
		self.unlock()
		return pp


	def push(self, msg):
		items = self.lock()
		for pp in items:
			pp.put_message([msg])
		self.unlock()



# 所有订阅点	
_all_pps = PullPoints()


class ListHandler(RequestHandler):
	def get(self):
		''' 列出所有订阅点？ '''
		pps = _all_pps.lock()
		self.write({'all':pps, 'result':'ok', 'info':'' })
		_all_pps.unlock()



class CreatePPHandler(RequestHandler):
	def get(self):
		''' 处理 create_pp '''
		pp = _all_pps.create()
		self.write( {'pid': pp.pid(), 'result':'ok', 'info':'' })



def run_async(func):
	@wraps(func)
	def async_func(*args, **kwargs):
		f = threading.Thread(target = func, args = args, kwargs = kwargs)
		f.start()
		return f
	return async_func



class EventHandler(RequestHandler):
	''' 处理 get, unsubscribe, seek, .... '''
	def get(self, pid, command):
		pp = _all_pps.get_pp(int(pid)) # pid 总是 int 类型 
		if not pp:
			self.write( {'result':'error', 'info':' pid NOT found' } )
		else:
			if command == 'pull':
				self.__pull(pp)
			elif command == 'unsubscribe':
				self.__unsubscribe(pp)
		

	@asynchronous
	@coroutine
	def __pull(self, pp):
		''' 如果有pending message，立即返回，否则最多等待 10秒 ..'''
		res = yield Task(self.__pull0, pp=pp)
		self.write(str(res)) # json 序列化 Message 时，会出问题 ...
		self.finish()


	@run_async
	def __pull0(self, callback, pp):
		# 这里阻塞等待 ....
		msgs = pp.get_message()
		result = { 'result':'ok', 'info':'', 'msgs': msgs }
		callback(result)



	def __unsubscribe(self, pp):
		''' 删除对应的 pp '''
		_all_pps.destroy(pp)
		self.write({'result':'ok', 'info':'unsubscribed' })



def make_app():
	return Application([
			url(r'/event/?', ListHandler),
			url(r'/event/create_pp', CreatePPHandler),
			url(r'/event/([0-9]+)/(.+)', EventHandler),
			])



if __name__ == '__main__':
	recver = LocalUdpRecver()
	recver.start()
	app = make_app()
	app.listen(10001)
	IOLoop.current().start()
	recver.join()
