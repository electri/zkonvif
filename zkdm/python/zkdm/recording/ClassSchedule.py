# _*_ coding: utf-8 _*_

import threading
import json
import time, sys, io
import urllib2

sys.path.append('../')
from common.utils import zkutils
from RecordingCommand import RecordingCommand
from LivingServer import StartLiving, StopLiving
_record_thread = []

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
        ret = json.load(io.open(r'../host/config.json', 'r', encoding='utf-8'))
        r = ret['regHbService']
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
        _rcmd.send_command('RecordCmd=StopRecord')
        time.sleep(0.5)
        _directory_name = 'RecordCmd=SetFileFolder&SubFileFolder=' + info['_directory_name']
        _rcmd.send_command(_directory_name)
        time.sleep(0.5)
        _course_info = 'RecordCmd=SetCourseInfo&Department=%s&Subject=%s&CourseName=%s&\
                Teacher=%s&Address=%s&DateTime=%s&Description=%s&Grade=%s'\
                %(info['_department'], info['_subject'],info['_course_name'],
                        info['_teacher'],info['_address'],info['_datetime'],info['_description'],info['_grade'])
        _rcmd.send_command(_course_info)
        time.sleep(0.5)
        _rcmd.send_command('RecordCmd=StartRecord')

    def _stop_record(self):
        '''
        停止录像任务
        '''
        _rcmd = RecordingCommand()
        _rcmd.send_command('RecordCmd=StopRecord')

    def _stop_execute_task(self):
        '''
        取消所有任务
        '''
        for thread in _record_thread:
            thread.cancel()

    def _apply_living(self,end_time):
        '''
        像平台申请直播
        '''
        _utils = zkutils()
        mac = _utils.mymac()
        resopnse = urllib2.urlopen(self.__mgrt_base_url+'livingStart?mac='+mac+'&endTime='+endtime,timeout=2)

    def _apply_stop_living(self):
        '''
        像平台申请停止直播
        '''
        _utils = zkutils()
        mac = _utils.mymac()
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

    def _analyse_data(self, data):
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

                thread =  threading.Timer(_start_delay_time,self._record_task,[info])
                thread.start()
                _record_thread.append(thread) 

            if _recording == 'true' and _stop_delay_time>0:
                stop_thread =  threading.Timer(_stop_delay_time,self._stop_record)
                stop_thread.start()
                _record_thread.append(stop_thread)

            if _living == 'true' and _start_delay_time>0:
                thread = threading.Timer(_start_delay_time,self._apply_living,[_stop_time])
                thread.start()
                _record_thread.append(thread)

            if _living == 'true' and _stop_delay_time>0:
                stop_thread = threading.Timer(_stop_delay_time,self._apply_stop_living)
                stop_thread.start()
                _record_thread.append(stop_thread)

            reload_thread = threading.Timer(1*3600, self.analyse_json)#1小时重新获取一次课表信息
            _record_thread.append(reload_thread)

    def analyse_json(self,ip,hosttype):
        rc = {}
        rc['result'] = 'ok'
        rc['info'] = ''
        try:      
            _utils = zkutils()
            mac = _utils.mymac()
            #mac = '00E04CC20811'
            data = ''
            try:
                response = urllib2.urlopen(self.__mgrt_base_url+'curriculum?mac=' + mac,timeout = 3)
                data = json.load(response)                
                with open('CourseInfo.json','w') as savefile:
                    json.dump(data,savefile)
            except Exception as err:
                print err
                data = {}
                course_info_file = file('CourseInfo.json')
                data = json.load(course_info_file)
            self._stop_execute_task()
            self._analyse_data(data)
        except Exception as err:
            print err
            rc['result'] = 'error'
            rc['info'] = str(err)
            return rc
          
        return rc
