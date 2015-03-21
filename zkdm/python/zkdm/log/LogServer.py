# coding: utf-8


from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application, url
from dbhlp import DBHlp
import time, json
import sys
import portalocker


sys.path.append('../')

VERSION = 0.91
VERSION_INFO = 'Log Service ...'


class HelpHandler(RequestHandler):
    def get(self):
        self.render('help.html')


class QueryHandler(RequestHandler):
    ''' 查询 '''
    def get(self):
        rc = {}
        rc['result'] = 'ok'
        rc['info'] = ''

        p = self.request.arguments
        project = self.__param('project', p)
        level = self.__param('level', p)
        stamp_begin = self.__param('stamp_begin', p)
        if stamp_begin is None:
            stamp_begin = str(time.time() - 600) # 缺省返回最近十分钟的日志
        stamp_end = self.__param('stamp_end', p)
        db = DBHlp()
        logs = db.query(project, level, stamp_begin, stamp_end)
        value = {}
        value['type'] = 'list'
        value['data'] = logs
        rc['value'] = value
        self.add_header('Access-Control-Allow-Origin', '*') # to enable cross domain calling
        self.write(rc)


    def __param(self, key, params):
        if key in params:
            value = params[key]
            v = value[0]
            if v == '':
                return None
        return None


# 只是为了支持 internal?command=exit, 可以优雅的结束 ...
_ioloop = IOLoop.instance()

class InternalHandler(RequestHandler):
    ''' 处理内部命令 '''
    def get(self):
        rc = {}
        rc['result'] = 'ok'
        rc['info'] = ''

        cmd = self.__param('command')
        if cmd is None:
            rc['result'] = 'err'
            rc['info'] = '"command" MUST be suppiled!'
            self.write(rc)
            return

        if cmd == 'version':
            ver = {}
            ver['version'] = VERSION
            ver['descr'] = VERSION_INFO
            data = {}
            data['type'] = 'version'
            data['data'] = ver
            rc['value'] = data
            self.write(rc)

        if cmd == 'exit':
            global _ioloop
            rc['info'] = 'exit!!!'
            rh.join()
            self.write(rc)
            _ioloop.stop()
        

    def __param(self, key):
        if key in self.request.arguments:
            return self.request.arguments[key][0]
        else:
            return None


def make_app():
    return Application([
            url(r'/log/query', QueryHandler),
            url(r'/log/help', HelpHandler),
            url(r'/log/internal', InternalHandler),
            ])


def main():
    pid_fname = "log.id"
    p = open(pid_fname, 'w')
    try:
        portalocker.lock(p, portalocker.LOCK_EX | portalocker.LOCK_NB)
    except:
        print 'ERR: only one instance can be started!!!'
        return

    app = make_app()
    app.listen(10005)
  
    # 日志服务就不去注册了
    #sds = [ {'type':'log', 'id':'0', 'url':'http://<ip>:10005/log'}, ]
    #rh = common.reght.RegHt(sds)
    _ioloop.start()

    # 结束 ..
    print 'Log service end ...'



if __name__ == '__main__':
    main()

