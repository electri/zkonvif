# coding: utf-8
import json
import thread, time
import urllib,urllib2,sys,io
from CardServer import livingS, ReslivingS
from RecordingCommand import RecordingCommand
from Check_CardLive import CardLive_Runing
from LogWriter import log_info


sys.path.append('../')
from common.utils import zkutils

def StartLiving(ip,mac,hosttype):
    rc = {}
    rc['result'] = 'ok'
    rc['info'] = ''
    if hosttype == 'x86':
        rc = _x86_rtmp_living(ip,mac)
    else:
        rc = _arm_rmtp_living(ip,hosttype)
    return rc

def _arm_rmtp_living(ip,hosttype):
    arg = "RecordCmd = RtmpUrlS&rtmp://192.168.12.117:51935/zonekey/sereamid0^rtmp://192.168.12.117:51935/zonekey/sereamid1^rtmp://192.168.12.117:51935/zonekey/sereamid2"
    print arg
    print ip
    _rcmd = RecordingCommand()
    rc=_rcmd.send_command(arg,ip)

    print rc

    rc = _rcmd.send_command('BroadCastCmd=StartBroadCast',ip)
    print rc

    rc = {}
    rc['result'] = 'ok'
    rc['info'] = ''
    return rc

def _x86_rtmp_living_data(mac):
    data = {}
    _utils = zkutils()
    #mac = _utils.mymac()
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

def _load_base_url():
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

def _error_code(code,content):
    rc = {}
    rc['result'] = 'ok'
    rc['info'] = ''
    if code == 101:
        rc['result'] = 'error'
        rc['info'] = 'NOT_SUPPORTED_METHOD'
        return rc
    elif code == 102:
        rc['result'] = 'error'
        rc['info'] = 'NO_PARAMETER'
        return rc
    elif code == 103:
        rc['result'] = 'error'
        rc['info'] = 'INVALID_PARMAMETER'
        return rc
    elif code  == 110:
        rc['result'] = 'error'
        rc['info'] = 'DB_ERROR'
        return rc
    elif code == 120:
        rc['result'] = 'error'
        rc['info'] = 'NO_VALID_SERVERS'
        return rc
    elif code == 150:
        rc['result'] = 'error'
        rc['info'] = 'SOCKET_ERROR'
        return rc
    elif code == 200:
        rc['result'] = 'error'
        rc['info'] = 'UNKNOWN_ERROR'
        return rc
    elif code == 122:
        rc['result'] = 'ok'
        urls = []
        urls = content['content']
        infos = []

        for url in urls:
            info = {}
            info['uid'] = url['stream_uid']
            info['rtmp_repeater'] = url['publish_url']
            if 'teacher' in url['stream_uid']:
                info['card_info'] = 'card0'
            if 'teacher_full' in url['stream_uid']:   
                info['card_info'] = 'card1'
            if 'student' in url['stream_uid']:
                info['card_info'] = 'card2'
            if 'student_full' in url['stream_uid']:               
                info['card_info'] = 'card3'
            if 'vga' in url['stream_uid']: 
                info['card_info'] = 'card4'
            if 'blackboard_writing' in url['stream_uid']:
                info['card_info'] = 'card5'
            if 'movie' in url['stream_uid']:   
                info['card_info'] = 'card6'

            infos.append(info)
        rc['info'] = infos
        return rc
    elif code == 120:
        rc['result'] = 'error'
        rc['info'] = 'all servers are shutdown or full,please check'
        return rc
    else:
        rc['result'] = 'error'        
        rc['info'] = 'UNKNOWN_ERROR'
        return rc        

def _x86_rtmp_living(ip,mac):
    rc = {}
    rc['result'] = 'ok'
    rc['info'] = ''

    if CardLive_Runing()==False:
        rc['result'] = 'ok'
        rc['info'] = 'cardlive.exe is not exit!'
        return rc

    try:
        middle_req = urllib2.urlopen( _load_base_url()+'getServerUrl?type=middle',timeout=2)
        middle_url =middle_req.read()

        log_info('middle_url:' + str(middle_url))

        req = urllib2.Request(middle_url+'/repeater/prepublishbatch')
        data = _x86_rtmp_living_data(mac)
        data = json.dumps(data)

        response = urllib2.urlopen(req,data)
        content = json.load(response)

        log_info('reponse_code' + content['response_code'])
        if content['response_code'] != 0:
            rc = _error_code(content['response_code'],content)
            return rc

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
        log_info('StartBroadCast')
        if rc['result'] == 'ok':
            rc['info'] = infos
    except Exception as err:
        print str(err)
        rc['result'] = 'error'
        rc['info'] = str(err)

    return rc

def StopLiving():
    _rcmd = RecordingCommand()
    rc=_rcmd.send_command('BroadCastCmd=StopBroadCast',ip)
    return rc

