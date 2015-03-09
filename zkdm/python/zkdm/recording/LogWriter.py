# coding: utf-8

import logging, os
import time

def log_info(content):
    '''保存信息类日志

    '''
    debug = False
    if debug == True:
        date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        dir = 'log/' + date
        if os.path.exists(dir):
            logging.basicConfig(filename=dir +'/log.log',level = logging.DEBUG)
        else:
            os.makedirs(dir)
            logging.basicConfig(filename=dir +'/log.log',level = logging.DEBUG)
        logging.info(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\0\0\0\0" + content)

def log_debug(content):
    '''保存调试类日志

    '''
    debut = False
    if debug == True:
        date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        dir = 'log/' + date
        if os.path.exists(dir):
            logging.basicConfig(filename=dir +'/log.log',level = logging.DEBUG)
        else:
            os.makedirs(dir)
            logging.basicConfig(filename=dir +'/log.log',level = logging.DEBUG)
        logging.DEBUG(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\0\0\0\0" + content)

if __name__ == '__main__':
    log_info('测试')



