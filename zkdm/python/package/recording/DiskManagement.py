# coding: utf-8

import os,sys
import time
from operator import itemgetter, attrgetter
import threading
import win32file
import shutil
sys.path.append('../')
from common.uty_log import log

def get_fs_info(caption = "D:"):
    '''
    获取磁盘信息
    '''
    try:
        # 有可能不在 d:
        sectorsPerCluster, bytesPerSector, numFreeClusters, totalNumClusters = win32file.GetDiskFreeSpace(caption)
        freespace = (numFreeClusters * sectorsPerCluster * bytesPerSector) /(1024 * 1024 * 1024)
    except:
        log("can't stat disk space of %s" % caption, project = 'recording', level = 2)
        freespace = 11

    if freespace<10:#小于10G的时候开始清理空间
        return True
    else:
        return False

def sort_cmp(a,b):
    '''
    比较函数
    '''
    return int(a['time'] - b['time'])

def dir_list_file(path = 'D:\RecordFile'):
    '''
    获取指定目录下的文件夹
    '''
    dir_list = []
    if os.path.exists(path):
        for dir in os.listdir(path):
            dir_path = path + '\\' + dir
            if os.path.isdir(dir_path):
                dir_info = {}
                dir_info['path'] = dir_path
                dir_info['time'] = os.path.getmtime(dir_path)
                dir_list.append(dir_info)

    dir_list.sort(cmp = sort_cmp)
    return dir_list

def del_dir_schedule():
    thread = threading.Timer(3600,del_dir_schedule) #1小时执行一次
    thread.start()
    if get_fs_info():
        dir_list = dir_list_file()
        while get_fs_info():
            if len(dir_list)==0:
                return
            try:
                log('del dir: %s' % dir_list[0]['path'], project = 'recording', level = 2)
                shutil.rmtree(dir_list[0]['path'],True)
            except Exception as error:
                print error
            dir_list.remove(dir_list[0])

