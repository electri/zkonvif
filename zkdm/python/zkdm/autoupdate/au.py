#!/usr/bin/python
# coding: utf-8
#
# @file: au.py
# @date: 2015-03-09
# @brief:
# @detail:
#
#################################################################

''' 类似 checkVersion，但解压到临时目录中 '''

import urllib2, zipfile, tempfile, os, filecmp, logging, shutil, sys, json
import conf_mc as cc


def checkVersion():
    #日志大于5M，删除
    try:
        if os.path.getsize("update.log") > 5000000:
            os.remove("update.log")
    except Exception, ex:
        pass

    #日志格式
    logging.basicConfig(level=logging.DEBUG,
               format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
               datefmt='%a, %d %b %Y %H:%M:%S',
               filename='update.log',
               filemode='a')

    #################################################################################################
    #定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    logging.debug("#################################################################################################")

    cs = cc.getconf_mulcast()
    try:
        conf = json.loads(cs)
    except:
        logging.error('json parse err')
        return False

    version_url = conf['AutoUpdate']['version']
    zip_url = conf['AutoUpdate']['package']

    logging.debug('to download %s' % version_url)
    if not __dlfile(version_url, 'tmp_version'):
        logging.error('can\'t download version file, to check url')
        return False

    logging.debug('to compare version')
    if os.path.isfile('local_version') and filecmp.cmp('local_version', 'tmp_version'):
        logging.debug('version NOT changed!')
        return False

    logging.debug('to download update zip package, from %s' % zip_url);
    if not __dlfile(zip_url, 'tmp_package.zip'):
        logging.error('can\'t download update package, to check url!!!')
        return False

    try:
        extract_path = tempfile.mkdtemp('.zonekey', 'au.')
        logging.debug('using temp path of %s' % extract_path)
    except:
        logging.error('can\'t create tmp path for extract?? to check disk free space!')
        return False

    try:
        logging.debug('to extract tmp_package.zip to %s' % extract_path)
        z = zipfile.ZipFile('tmp_package.zip')
        z.extractall(extract_path)
    except:
        logging.error('extract fault!!!')
        shutil.rmtree(extract_path) # 临时目录必须主动删除
        return False

    logging.debug('to load install script from %s/%s' % (extract_path, 'install.py'))

    curr_path = os.getcwd()
    os.chdir(extract_path)
    sys.path.append('.') # 增加临时目录

    mod = __load_script('install.py')
    if mod is None:
        os.chdir(curr_path)
        logging.error('can\'t load install script ...')
        shutil.rmtree(extract_path) # 临时目录必须主动删除
        return False

    try:
        logging.debug('to execute install ...')
        func = getattr(mod, 'setup') # install.py 中，必须实现 setup() 函数
        if not func(): # setup() 返回 False，一般是因为本次更新不包含本机
            logging.debug('NOT include me')
            os.chdir(curr_path)
            shutil.rmtree(extract_path)
            try:
                os.remove('local_version')
            except:
                pass
            try:
                os.rename('tmp_version', 'local_version')
            except:
                pass
            return False
    except:
        os.chdir(curr_path)
        logging.error('can\'t exec ')
        shutil.rmtree(extract_path) # 临时目录必须主动删除
        return False

    os.chdir(curr_path)
    logging.info('update successful')
    shutil.rmtree(extract_path)

    try:
        os.remove('local_version')
    except:
        pass

    try:
        os.rename('tmp_version', 'local_version')
    except Exception as e:
        print e
        return False

    return True



def __dlfile(url, fname):
    try:
        rf = urllib2.urlopen(url)
        with open(fname, 'wb') as lf:
            lf.write(rf.read())
        return True
    except:
        return False


def __load_script(fname):
    ''' 此时当前目录下就应该有 fname '''
    try:
        import imp
        mod = imp.load_source('installer', fname)
        return mod
    except:
        logging.error('can\'t load %s' % fname)
        return None


if __name__ == '__main__':
    checkVersion() 

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

