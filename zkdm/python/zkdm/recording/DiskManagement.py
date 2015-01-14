# coding: utf-8

import os,sys
import time
from operator import itemgetter, attrgetter
import wmi

def get_fs_info(caption = "C:"):
    '''
    获取文件信息
    '''
    temp_list = []
    my_wmi = wmi.WMI()
    for physical_disk in my_wmi.Win32_DiskDrive():
        for partition in physical_disk.associators('Win32_DiskDriveToDiskPartition'):
            for logical_disk in partition.associators('Win32_LogicalDiskToPartition'):
                if logical_disk.Caption == caption:
                    free_space = int(logical_disk.FreeSpace)/1024/1024/1024
                    percent = int(100.0*(int(logical_disk.Size)-int(logical_disk.FreeSpace))/int(logical_disk.Size))
                    if free_space < 10 or percent>90:
                        return True
                    else:
                        return False
def sort_cmp(a,b):
    return int(a['time'] - b['time'])

def dir_list_file(path = 'C:\RecordFile'):
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

    print dir_list
    #sorted(dir_list, key=itemgetter(1))
    dir_list.sort(cmp = sort_cmp)
    print dir_list

dir_list_file()
