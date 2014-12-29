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
    data['group_id'] = mac
    move = {}
    move['uid'] = mac + '_Move'
    resource1 = {}
    resource1['uid'] = mac + '_Teacher'
    resource2 = {}
    resource2['uid'] = mac + '_Student'
    resource3 = {}
    resource3['uid'] = mac + '_Full'
    resource4 = {}
    resource4['uid'] = mac + '_Teacher1'
    resource5 = {}
    resource5['uid'] = mac + '_Teache2r'
    resource6 = {}
    resource6['uid'] = mac + '_Teacher3'
    data['uids'] = [move,resource1,resource2,resource3,resource4,resource5,resource6]
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
        move_url = ip = port = app = ''

        for url in urls:
            if 'Move' in url['rtmp_repeater']:
                move_url = url['rtmp_repeater']
                url = move_url
                url = url[7:]
                ip = url.split(':')[0]
                url = url[len(ip)+1:]
                port = url.split('/')[0]
                url =url[len(port)+1:]
                app = url.split('/')[0]

        livingS(move_url)
        ReslivingS(ip,port,ap)
        time.sleep(1)
        _rcmd = RecordingCommand()
        rc=_rcmd.send_command('BroadCastCmd=StartBroadCast',ip)
        if rc['result'] == 'ok':
            rc['info'] = url
    except Exception as err:
        rc['result'] = 'error'
        rc['info'] = str(err)

    return rc

def StopLiving():
    _rcmd = RecordingCommand()
    rc=_rcmd.send_command('BroadCastCmd=StopBroadCast',ip)
    return rc

