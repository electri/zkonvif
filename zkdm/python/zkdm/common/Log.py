# coding: utf-8

import urllib2, json, time, threading, Queue

class _WorkingThread(threading.Thread):
    def __init__(self, base_url):
        threading.Thread.__init__(self)
        self.__quit = False
        self.__base_url = base_url
        self.__queue = Queue.Queue()
        self.start()

    def run(self):
        while not self.__quit:
            log = self.__queue.get()
            opener = urllib2.build_opener(urllib2.HTTPHandler)
            req = urllib2.Request(self.__base_url + '/save', log)
            req.add_header('Content-Type', 'application/json')
            req.get_method = lambda: 'PUT'
            try:
                url = opener.open(req)
            except:
                #print 'ERR: cannot put to:', self.__base_url
                pass

    def append(self, log):
        ''' 追加新的日志，非阻塞 '''
        self.__queue.put_nowait(log)


    def join(self):
        self.__quit = True;
        self.append('')
        threading.Thread.join(self)


class Log:
    ''' 为了方便的使用 LogServer
    '''
    def __init__(self, project, base_url = None):
        self.__project = project
        if base_url is None:
            self.__base_url = 'http://127.0.0.1:10005/log'
        else:
            self.__base_url = base_url
        self.__working = _WorkingThread(self.__base_url)


    def log(self, content, level = 99):
        ''' 对于日志来说，不能阻塞本地调用，所有简单的放到一个
            fifo 中，由后台工作线程负责提交到 LogServer
        '''
        body = self.__build_body(level, content)
        self.__working.append(body)

    
    def __build_body(self, level, content):
        ''' 构造 json 数据，并返回,
            注意，字符串必须能够 json.loads()，要求使用双引号 
        '''
        data = {}
        data["project"] = self.__project
        data["level"] = level
        data["stamp"] = int(time.time())
        data["content"] = content

        # XXX: json 的 dumps 支持 dict, list, tuple, str, unicode, int, double, long, True
        #            False, None
        #             不支持 object ....
        s = json.dumps(data)
        return s




if __name__ == '__main__':
    log = Log('test project')
    log.log('test info ...')
    

