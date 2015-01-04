# coding: utf-8
import json
import thread, time
import urllib,urllib2,sys
from CardServer import livingS, ReslivingS
from RecordingCommand import RecordingCommand

sys.path.append('../')
from common.utils import zkutils

def StartLiving(ip,hosttype):
    rc = {}
    rc['result'] = 'ok'
    rc['info'] = ''
    if hosttype == 'x86':
        rc = _x86_rtmp_living(ip)
    else:
        rc = _arm_rmtp_living(ip)
    return rc

def _arm_rmtp_living(ip):
    rc = {}
    rc['result'] = 'ok'
    rc['info'] = ''
    return rc

def _x86_rtmp_living_data():
    data = {}
    _utils = zkutils()
    mac = _utils.mymac()
    #mac = '00E04CC20811'
    mac = mac.lower()
    data['group_id'] = mac
    move = {}
    move['uid'] = mac + '_movie'

    resource1 = {}
    resource1['uid'] = mac + '_teacher'
    resource2 = {}
    resource2['uid'] = mac + '_student'
    resource3 = {}
    resource3['uid'] = mac + '_vga'
    resource4 = {}
    resource4['uid'] = mac + '_teacher_full'
    resource5 = {}
    resource5['uid'] = mac + '_student_full'
    resource6 = {}
    resource6['uid'] = mac + '_blackboard_writing'
    data['uids'] = [resource1,resource2,resource3]#保留三路资源
    return data

def _x86_rtmp_living(ip):
    rc = {}
    rc['result'] = 'ok'
    rc['info'] = ''

    try:
        req = urllib2.Request('http://192.168.12.111:50001/repeater/prepublishbatch')
        data = _x86_rtmp_living_data()
        data = json.dumps(data)

        response = urllib2.urlopen(req,data)
        content = json.load(response)
        urls = []
        urls = content['content']
        movie_url = rtmp_ip = port = app = ''
        infos = []

        for url in urls:
            info = {}
            info['uid'] = url['uid']
            info['rtmp_repeater'] = url['rtmp_repeater']
            if 'teacher' in url['uid']:
                info['card_info'] = 'card0'
            if 'teacher_full' in url['uid']:   
                info['card_info'] = 'card1'
            if 'student' in url['uid']:
                info['card_info'] = 'card2'
            if 'student_full' in url['uid']:               
                info['card_info'] = 'card3'
            if 'vga' in url['uid']: 
                info['card_info'] = 'card4'
            if 'blackboard_writing' in url['uid']:
                info['card_info'] = 'card5'
            if 'movie' in url['uid']:   
                info['card_info'] = 'card6'

            infos.append(info)

            if 'teacher' in url['rtmp_repeater']:
                #movie_url = url['rtmp_repeater']
                #livingS(movie_url)
                url = url['rtmp_repeater']
                url = url[7:]
                rtmp_ip = url.split(':')[0]
                url = url[len(rtmp_ip)+1:]
                port = url.split('/')[0]
                url =url[len(port)+1:]
                app = url.split('/')[0]

        ReslivingS(rtmp_ip,port,app)
        time.sleep(1)
        _rcmd = RecordingCommand()
        rc=_rcmd.send_command('BroadCastCmd=StartBroadCast',ip)
        if rc['result'] == 'ok':
            rc['info'] = infos
    except Exception as err:
        rc['result'] = 'error'
        rc['info'] = str(err)

    return rc

def StopLiving():
    _rcmd = RecordingCommand()
    rc=_rcmd.send_command('BroadCastCmd=StopBroadCast',ip)
    return rc

