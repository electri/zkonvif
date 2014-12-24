# _*_ coding: utf-8 _*_

import threading
import json
import time, sys
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
        if mgrt_baseurl is None:
            mgrt_base_url = self._load_base_url()
        slef.__mgrt_base_url = mgrt_base_url

    _record_thread = []

    def _load_base_url(self):
        ret = json.load(io.open(r'../host/config.json', 'r', encoding='utf-8'))
        r = ret['regHbService']
        if ' ' in r['sip'] or ' ' in r['sport']:
            raise Exception("include ' '")
        if r['sip'] == '' or r['sport'] == '':
            raise Exception("include''")
        return 'http://%s:%s/deviceService/'%(r['sip'],r['sport'])
    
    def _record_task(self,info):
        _rcmd = RecordingCommand()

        _rcmd.send_command('RecordCmd=StopRecord')
        time.sleep(0.5)
        _directory_name = 'RecordCmd=SetFileFolder&SubFileFolder=' + _directory_name
        _rcmd.send_command(_directory_name)
        time.sleep(0.5)
        _course_info = 'RecordCmd=SetCourseInfo&Department=%s&Subject=%s&CourseName=%s&\
                Teacher=%s&Address=%s&DateTime=%s&Description=%s&Grade=%s'\
                %(info[_department], info[_subject],info[_course_name],
                        info[_teacher],info[_address],info[_datetime],info[_description],info[_grade])
        _rcmd.send_command(_course_info)
        time.sleep(0.5)
        _rcmd.send_command('RecordCmd=StartRecord')

    def _stop_record(self):
         _rcmd = RecordingCommand()
         _rcmd.send_command('RecordCmd=StopRecord')

    def _stop_execute_task(self):
        for thread in _record_thread:
            thread.cancel()
    def test(self):
        print 'testsertrst'

    def _apply_living(self,endime):
        _utils = zkutils()
        mac = utils.mymac()
        resopnse = urlib2.urlopen(self.__mgrt_base_url+'/livingStart?mac='+mac+'&endTime='+endtime)


    def _analyse_json(self):
        rc = {}
        rc['result'] = 'ok'
        rc['info'] = ''
        try:      
            _utils = zkutils()
            mac = _utils.mymac()
            data = ''
            try:
                response = urllib2.urlopen(self.__mgrt_base_url+'/curriculum?mac=' + mac)
                data = json.load(response)
                with open('CourseInfo.json','w') as savefile:
                    json.dump(data,savefile)
            except Exception as err:
                f = file('CourseInfo.json')
                data = json.load(f)
            print data

            self._stop_execute_task()
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
                _start_time = time.strptime(_start_time,'%Y-%m-%d %H:%M:%S')
                _stop_time = time.strptime(_stop_time,'%Y-%m-%d %H:%M:%S')

                if _start_time.tm_mday == _now_time.tm_mday and\
                        _start_time.tm_year == _now_time.tm_year \
                        and _start_time.tm_mon == _now_time.tm_mon:                    
                
                    _delay_time = (_start_time.tm_hour-_now_time.tm_hour)*3600 \
                            + (_start_time.tm_min - _now_time.tm_min)*60\
                            + (_start_time.tm_sec - _now_time.tm_sec)
                    _stop_delay_time= (_stop_time.tm_hour-_now_time.tm_hour)*3600 \
                            + (_stop_time.tm_min - _now_time.tm_min)*60\
                            + (_stop_time.tm_sec - _now_time.tm_sec) 

                    if _recording == True and _delay_time>0:
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

                        thread =  threading.Timer(_delay_time,_record_task,[info])
                        _record_thread.append(thread)    

                    if _recording == True and _stop_delay_time>0:
                        stop_thread =  threading.Timer(_stop_delay_time,_stop_record)
                        _record_thread.append(stop_thread)

                    if _living == True and _delay_time>0:
                        thread = threading.Timer(_delay_time,_apply_living)
                        _record_thread.append(thread)

                    if _living == True and _stop_delay_time>0:
                        stop_thread = threading.Timer(_stop_delay_time,StopLiving)
                        _record_thread.append(stop_thread)

        except Exception as err:
            rc['result'] = 'error'
            rc['info'] = str(err)
            print rc
            return rc
          
        return rc
