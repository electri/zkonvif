# coding: utf-8
# 
# @file: DirectoryMonitor.py
# @date: 2014-09-15
# @brief: 监视本地文件变化，这里主要是为了监视 my.tab 的修改
# @detail:
#
#################################################################


from watchdog.observers import Observer
from watchdog.events import *
import threading, time, os, sched


class MyEventHandler(FileSystemEventHandler):
    ''' 监视目录变化，当 fname 修改后，通知 ... '''
    def __init__(self, fname, when_changed_callable):
        self.__fname = fname
        self.__f_changed = when_changed_callable


    def on_modified(self, event):
        if os.path.isfile(event.src_path):
            if os.path.split(event.src_path)[1] == os.path.split(self.__fname)[1]:
                if self.__f_changed:
                    self.__f_changed()
            



__observer = None

def start_monitor(path, fname, callback):
    global __observer
    me = MyEventHandler(fname, callback)
    __observer = Observer()
    __observer.schedule(me, path, False)
    __observer.start()


def stop_monitor():
    if __observer:
        __observer.stop()
        __observer.join()
    __observer = None



def dummy_callback():
    print 'my.tab changed!!!!'


if __name__ == '__main__':
    start_monitor('.', 'my.tab', dummy_callback)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_monitor()



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

