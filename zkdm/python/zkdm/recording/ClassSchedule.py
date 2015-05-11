# _*_ coding: utf-8 _*_

import threading
import json
import time, sys, io
import urllib2

sys.path.append('../')
from common.utils import zkutils
from RecordingCommand import RecordingCommand
from LivingServer import StartLiving, StopLiving
from common.uty_log import log
from common.conf_mc import getconf_mulcast

_record_thread = []

# 全局配置
global_conf = {
	"NSService": {
		"sip" : "172.16.30.251",
		"sport" :"8080" 
	}
}

gcs = getconf_mulcast()

try:
    conf = json.loads(gcs)
    global_conf = conf
except:
    pass


class Schedule():
    '''
    课表解析
    '''
    def __init__(self,mgrt_base_url = None):
        if mgrt_base_url is None:
            mgrt_base_url = self._load_base_url()
        self.__mgrt_base_url = mgrt_base_url
        print self.__mgrt_base_url

    _record_thread = []

    def _load_base_url(self):
        '''
        平台地址
        '''
        ret = global_conf
        r = ret['NSService']
        if ' ' in r['sip'] or ' ' in r['sport']:
            raise Exception("include ' '")
        if r['sip'] == '' or r['sport'] == '':
            raise Exception("include''")
        return 'http://%s:%s/deviceService/'%(r['sip'],r['sport'])
    
    def _record_task(self,info):
        '''
        开始录像任务
        '''
        print 'start record_task'
        _rcmd = RecordingCommand()
        _rcmd.send_command('RecordCmd=StopRecord', info['_ip'])
        time.sleep(0.2)
        if info['_record_mode'].lower() == 'all':
            _rcmd.send_command('RecordCmd=SetRecordMode&RecordMode=All', info['_ip'])
        elif info['_record_mode'].lower() == 'resource':
            _rcmd.send_command('RecordCmd=SetRecordMode&RecordMode=Resource', info['_ip'])
        elif info['_record_mode'].lower() == 'movie':
            _rcmd.send_command('RecordCmd=SetRecordMode&RecordMode=Movie', info['_ip'])
        time.sleep(0.2)
        _directory_name = 'RecordCmd=SetFileFolder&SubFileFolder=' + info['_directory_name']
        _rcmd.send_command(_directory_name, info['_ip'])
        time.sleep(0.2)
        _course_info = 'RecordCmd=SetCourseInfo&Department=%s&Subject=%s&CourseName=%s&\
                Teacher=%s&Address=%s&DateTime=%s&Description=%s&Grade=%s'\
                %(info['_department'], info['_subject'],info['_course_name'],
                        info['_teacher'],info['_address'],info['_datetime'],info['_description'],info['_grade'])
        _rcmd.send_command(_course_info, info['_ip'])
        time.sleep(0.2)
        _rcmd.send_command('RecordCmd=StartRecord', info['_ip'])

    def _stop_record(self, info):
        '''
        停止录像任务
        '''
        _rcmd = RecordingCommand()
        _rcmd.send_command('RecordCmd=StopRecord', info['_ip'])

    def _stop_execute_task(self,mac):
        '''
        取消所有任务
        '''
        for thread in _record_thread:
            if thread.name == mac:
                thread.cancel()

    def _apply_living(self, info):
        '''
        像平台申请直播
        '''
        mac = info['_mac']
        end_time = info['_stop_time']
        resopnse = urllib2.urlopen(self.__mgrt_base_url+'livingStart?mac='+mac+'&endTime='+endtime,timeout=2)

    def _apply_stop_living(self,info):
        '''
        像平台申请停止直播
        '''
        mac = info['_mac']
        resopnse = urllib2.urlopen(self.__mgrt_base_url+'living?mac='+mac+'&para=stop',timeout=2)

    def _analyse_time(self,give_time):
        '''
        分析是否当前任务
        '''
        _now_time = time.localtime(time.time())
        _give_time = time.strptime(give_time,'%Y-%m-%d %H:%M:%S')
        _delay_time = 0

        if _give_time.tm_year == _now_time.tm_year and _give_time.tm_mon == _now_time.tm_mon \
                and _give_time.tm_mday == _now_time.tm_mday:
            _hour = (_give_time.tm_hour - _now_time.tm_hour)*3600
            _min = (_give_time.tm_min - _now_time.tm_min)*60
            _sec = (_give_time.tm_sec - _now_time.tm_sec)
            _delay_time = _hour + _min + _sec
        else:
            _delay_time = -1
        return _delay_time

    def _analyse_data(self, data, ip, mac):
        global _record_thread
        _record_thread = []

        for i in range(len(data['ScheduleTask'])):
            _directory_name = data['ScheduleTask'][i]['directoryName']
            _recording = data['ScheduleTask'][i]['recording']
            _record_mode = data['ScheduleTask'][i]['recordMode']
            _start_time = data['ScheduleTask'][i]['startTime']
            _stop_time = data['ScheduleTask'][i]['stopTime']
            _living = data['ScheduleTask'][i]['living']
            _living_mode = data['ScheduleTask'][i]['livingMode']

            _department = data['ScheduleTask'][i]['courseInfo']['department']
            _subject = data['ScheduleTask'][i]['courseInfo']['subject']
            _course_name = data['ScheduleTask'][i]['courseInfo']['courseName']
            _teacher = data['ScheduleTask'][i]['courseInfo']['teacher']
            _grade = data['ScheduleTask'][i]['courseInfo']['grade']
            _address = data['ScheduleTask'][i]['courseInfo']['address']
            _description = data['ScheduleTask'][i]['courseInfo']['description']


            _now_time = time.localtime(time.time())
            _start_delay_time = self._analyse_time(_start_time)
            _stop_delay_time = self._analyse_time(_stop_time)


            if _recording == 'true' and _start_delay_time>0:
                info = {}
                info['_directory_name'] = _directory_name
                info['_record_mode'] = _record_mode
                info['_stop_time'] = _stop_time
                info['_department'] = _department
                info['_subject'] = _subject
                info['_course_name'] = _course_name
                info['_teacher'] = _teacher
                info['_grade'] = _grade
                info['_address'] = _address
                info['_living'] = _living
                info['_living_mode'] = _living_mode
                info['_datetime'] = _start_time
                info['_description'] = _description
                info['_ip'] = ip

                thread =  threading.Timer(_start_delay_time,self._record_task,[info])
                thread.setName(mac)
                thread.start()
                _record_thread.append(thread) 

            if _recording == 'true' and _stop_delay_time>0:
                info = {}
                info['_ip'] = ip
                stop_thread =  threading.Timer(_stop_delay_time,self._stop_record,[info])
                stop_thread.setName(mac)
                stop_thread.start()
                _record_thread.append(stop_thread)

            if _living == 'true' and _start_delay_time>0:
                info = {}
                info['_mac'] = mac
                info['_stop_time'] = _stop_time
                thread = threading.Timer(_start_delay_time,self._apply_living,[info])
                thread.setName(mac)
                thread.start()
                _record_thread.append(thread)

            if _living == 'true' and _stop_delay_time>0:
                info = {}
                info['_mac'] = mac
                stop_thread = threading.Timer(_stop_delay_time,self._apply_stop_living,[info])
                stop_thread.setName(mac)
                stop_thread.start()
                _record_thread.append(stop_thread)

    def restart_rtmp_living(self,ip='127.0.0.1',hosttype = 'x86'):
        reload_thread = threading.Timer(3*3600, self.restart_rtmp_living)#3小时重新发起直播
        reload_thread.start()
        try:
            _rcmd = RecordingCommand()
            #info = _rcmd.send_command('RecordCmd=QueryRAllInfo')
            #if 'LivingStart' in info['info']:
            _rcmd.send_command('BroadCastCmd=StopBroadCast')
            time.sleep(3)
            _rcmd.send_command('BroadCastCmd=StartBroadCast')
        except Exception as error:
            print str(error)

    

    def set_recording_dir(self,ip='127.0.0.1',hosttype='x86'):
        set_thread = threading.Timer(600, self.set_recording_dir)
        set_thread.start()
        try:
            _rcmd = RecordingCommand()
            _rcmd.send_command('RecordCmd=SetFileProperty&FileFormat=mp4&TotalFilePath=D:/RecordFile')

        except Exception as error:
            print str(error)

    def analyse_json(self, ip = '127.0.0.1', mac = ''):
        log('ClassSchedule.analyse_json: starting ..., ip=%s, mac=%s' % (ip, mac), project = 'recording')

        reload_thread = threading.Timer(3600, self.analyse_json, (ip, mac))#1小时重新获取一次课表信息
        reload_thread.start()
        print ip,mac
        rc = {}
        rc['result'] = 'ok'
        rc['info'] = ''
        try:      
            data = ''
            try:
                url = self.__mgrt_base_url+'curriculum?mac=' + mac 
                log('ClassSchedule.analyse: try download cs from %s' % url, project = 'recording')
                response = urllib2.urlopen(url, timeout = 3)
                data = json.load(response)
                with open(mac + 'CourseInfo.json','w') as savefile:
                    json.dump(data,savefile)
            except Exception as err:
                log('ClassSchedule.analyse: download cs err, just load local??', project = 'recording', level = 1)
                data = {}
                course_info_file = file(mac + 'CourseInfo.json')
                data = json.load(course_info_file)
            self._stop_execute_task(mac)
            self._analyse_data(data, ip, mac)
        except Exception as err:
            print err
            rc['result'] = 'error'
            rc['info'] = str(err)
            return rc
          
        return rc

