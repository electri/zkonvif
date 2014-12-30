# -*- coding: utf-8 -*- 

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import socket

from tornado.options import define, options
from tornado.web import RequestHandler, Application, url

from suds.client import Client


def _param(req, key):
    if key in req.request.arguments:
        return req.request.arguments
    else:
        return None

def set_resource_info(data):
    try:
        resource_info = client.factory.create('ns0:ResourceInfo')  
        for i in data['ResourceList']:
            resource = client.factory.create('ns0:Resource')

            if hasattr(i, 'CardName'):
                resource['CardName'] = i['CardName']
            else:
                resource['CardName'] = None

            if hasattr(i, 'CardPort'):
                resource['CardPort'] = i['CardPort']
            else:
                resource['CardPort'] = None   

            if hasattr(i, 'IsUse'):
                resource['IsUse'] = i['IsUse']
            else:
                resource['IsUse'] = None    

            if hasattr(i, 'IsLock'):
                resource['IsLock'] = i['IsLock']
            else:
                resource['IsLock'] = None    

            if hasattr(i, 'BitRate'):
                resource['BitRate'] = i['BitRate']
            else:
                resource['BitRate'] = None    

            if hasattr(i, 'FrameRate'):
                resource['FrameRate'] = i['FrameRate']
            else:
                resource['FrameRate'] = None    

            if hasattr(i, 'Format'):
                resource['Format'] = i['Format']
            else:
                resource['Format'] = None    

            if hasattr(i, 'DefaultSceneName'):
                resource['DefaultSceneName'] = i['DefaultSceneName']
            else:
                resource['DefaultSceneName'] = None    

            if hasattr(i, 'Volume'):
                resource['Volume'] = i['Volume']
            else:
                resource['Volume'] = None    

            if hasattr(i, 'PhysicalAdress'):
                resource['PhysicalAdress'] = i['PhysicalAdress']
            else:
                resource['PhysicalAdress'] = None   

            if hasattr(i, 'GopSize'):
                resource['GopSize'] = i['GopSize']
            else:
                resource['GopSize'] = None  

            if hasattr(i, 'RecordName'):
                resource['RecordName'] = i['RecordName']
            else:
                resource['RecordName'] = None

            if hasattr(i, 'TrackNumber'):
                resource['TrackNumber'] = i['TrackNumber']
            else:
                resource['TrackNumber'] = None

            if hasattr(i, 'CardType'):
                resource['CardType'] = i['CardType']
            else:
                resource['CardType'] = None

            if hasattr(i, 'Deinterlace_Enable'):
                resource['Deinterlace_Enable'] = i['Deinterlace_Enable']
            else:
                resource['Deinterlace_Enable'] = None  

            if hasattr(i, 'Deinterlace_Type'):
                resource['Deinterlace_Type'] = i['Deinterlace_Type']
            else:
                resource['Deinterlace_Type'] = None

            if hasattr(i, 'VideoWidth'):
                resource['VideoWidth'] = i['VideoWidth']
            else:
                resource['VideoWidth'] = None

            if hasattr(i, 'VideoHeight'):
                resource['VideoHeight'] = i['VideoHeight']
            else:
                resource['VideoHeight'] = None  

            if hasattr(i, 'InputAudioType'):
                resource['InputAudioType'] = i['InputAudioType']
            else:
                resource['InputAudioType'] = None  

            if hasattr(i, 'InputVideoType'):
                resource['InputVideoType'] = i['InputVideoType']
            else:
                resource['InputVideoType'] = None

            if hasattr(i, 'VideoEncoderType'):
                resource['VideoEncoderType'] = i['VideoEncoderType']
            else:
                resource['VideoEncoderType'] = None

            if hasattr(i, 'AudioEncoderType'):
                resource['AudioEncoderType'] = i['AudioEncoderType']
            else:
                resource['AudioEncoderType'] = None

            if hasattr(i, 'BFrame'):
                resource['BFrame'] = i['BFrame']
            else:
                resource['BFrame'] = None  

            if hasattr(i, 'RecordProfile'):
                resource['RecordProfile'] = i['RecordProfile']
            else:
                resource['RecordProfile'] = None

            if hasattr(i, 'RecordLevel'):
                resource['RecordLevel'] = i['RecordLevel']
            else:
                resource['RecordLevel'] = None

            if hasattr(i, 'RecordComlexity'):
                resource['RecordComlexity'] = i['RecordComlexity']
            else:                
                resource['RecordComlexity'] = None

            if hasattr(i, 'IsRecord'):
                resource['IsRecord'] = i['IsRecord']
            else:                
                resource['IsRecord'] = None

            resource_info.ResourceList[0].append(resource)
        client.service.ResourceListS(resource_info)
        print resource_info
        return True
    except Exception as error:
        return str(error)

def get_resource_info(method):
    rc={}
    rc['result'] = 'ok'
    rc['info'] = ''
    if method=='ResourceList':
        resource_list = client.service.ResourceList()['message']['ResourceList'][0]
    else:
        resource_list = client.service.ResourceListD()['message']['ResourceList'][0]

    l={'ResourceList':[]}

    for i in range(0,len(resource_list)):         
        resource = {}            
            
        if hasattr(resource_list[i], 'CardName'):
            resource['CardName'] = resource_list[i]['CardName']
        else:
            resource['CardName'] = ''            
            
        if hasattr(resource_list[i], 'CardPort'):
            resource['CardPort'] = resource_list[i]['CardPort']
        else:
            resource['CardPort'] = ''                        
            
        if hasattr(resource_list[i], 'IsUse'):
            resource['IsUse'] = resource_list[i]['IsUse']
        else:
            resource['IsUse'] = ''            
            
        if hasattr(resource_list[i], 'IsLock'):
            resource['IsLock'] = resource_list[i]['IsLock']
        else:
            resource['IsLock'] = ''

        if hasattr(resource_list[i], 'BitRate'):
            resource['BitRate'] = resource_list[i]['BitRate']
        else:
            resource['BitRate'] = ''            
            
        if hasattr(resource_list[i], 'FrameRate'):
            resource['FrameRate'] = resource_list[i]['FrameRate']
        else:
            resource['FrameRate'] = ''

        if hasattr(resource_list[i], 'Format'):
            resource['Format'] = resource_list[i]['Format']
        else:
            resource['Format'] = ''                     

        if hasattr(resource_list[i], 'DefaultSceneName'):
            resource['DefaultSceneName'] = resource_list[i]['DefaultSceneName']
        else:
            resource['DefaultSceneName'] = ''

        if hasattr(resource_list[i], 'Volume'):
            resource['Volume'] = resource_list[i]['Volume']
        else:
            resource['Volume'] = ''

        if hasattr(resource_list[i], 'PhysicalAdress'):
            resource['PhysicalAdress'] = resource_list[i]['PhysicalAdress']
        else:
            resource['PhysicalAdress'] = ''

        if hasattr(resource_list[i], 'GopSize'):
            resource['GopSize'] = resource_list[i]['GopSize']
        else:
            resource['GopSize'] = ''

        if hasattr(resource_list[i], 'RecordName'):
            resource['RecordName'] = resource_list[i]['RecordName']
        else:
            resource['RecordName'] = ''

        if hasattr(resource_list[i], 'TrackNumber'):
            resource['TrackNumber'] = resource_list[i]['TrackNumber']
        else:
            resource['TrackNumber'] = ''

        if hasattr(resource_list[i], 'CardType'):
            resource['CardType'] = resource_list[i]['CardType']
        else:
            resource['CardType'] = ''

        if hasattr(resource_list[i], 'Deinterlace_Enable'):
            resource['Deinterlace_Enable'] = resource_list[i]['Deinterlace_Enable']
        else:
            resource['Deinterlace_Enable'] = ''           

        if hasattr(resource_list[i], 'Deinterlace_Type'):
            resource['Deinterlace_Type'] = resource_list[i]['Deinterlace_Type']
        else:
            resource['Deinterlace_Type'] = ''

        if hasattr(resource_list[i], 'VideoWidth'):
            resource['VideoWidth'] = resource_list[i]['VideoWidth']
        else:
            resource['VideoWidth'] = ''

        if hasattr(resource_list[i], 'VideoHeight'):
            resource['VideoHeight'] = resource_list[i]['VideoHeight']
        else:
            resource['VideoHeight'] = ''

        if hasattr(resource_list[i], 'InputVideoType'):
            resource['InputVideoType'] = resource_list[i]['InputVideoType']
        else:
            resource['InputVideoType'] = ''

        if hasattr(resource_list[i], 'InputAudioType'):
            resource['InputAudioType'] = resource_list[i]['InputAudioType']
        else:
            resource['InputAudioType'] = ''

        if hasattr(resource_list[i], 'VideoEncoderType'):
            resource['VideoEncoderType'] = resource_list[i]['VideoEncoderType']
        else:
            resource['VideoEncoderType'] = ''

        if hasattr(resource_list[i], 'AudioEncoderType'):
            resource['AudioEncoderType'] = resource_list[i]['AudioEncoderType']
        else:
            resource['AudioEncoderType'] = ''

        if hasattr(resource_list[i], 'BFrame'):
            resource['BFrame'] = resource_list[i]['BFrame']
        else:
            resource['BFrame'] = ''

        if hasattr(resource_list[i], 'RecordProfile'):
            resource['RecordProfile'] = resource_list[i]['RecordProfile']
        else:
            resource['RecordProfile'] = ''

        if hasattr(resource_list[i], 'RecordLevel'):
            resource['RecordLevel'] = resource_list[i]['RecordLevel']
        else:
            resource['RecordLevel'] = ''
            
        if hasattr(resource_list[i], 'RecordEntropy'):
            resource['RecordEntropy'] = resource_list[i]['RecordEntropy']
        else:
            resource['RecordEntropy'] = ''

        if hasattr(resource_list[i], 'RecordComlexity'):
            resource['RecordComlexity'] = resource_list[i]['RecordComlexity']
        else:
            resource['RecordComlexity'] = ''

        if hasattr(resource_list[i], 'IsRecord'):
            resource['IsRecord'] = resource_list[i]['IsRecord']
        else:
            resource['IsRecord'] = ''

        l['ResourceList'].append(resource)

    rc['info']=l
    return rc

client=None

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Use the /card/help for more help !")

class HelpHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('card_help.html')

class ResourceListHandler(tornado.web.RequestHandler):
    def get(self):
        rc = {}
        rc = get_resource_info('ResourceList')
        self.write(rc)   

class ResourceListDHandler(tornado.web.RequestHandler):
    def get(self):
        rc = {}
        rc = get_resource_info('ResourceListD')
        self.write(rc)  

class ResourceListSHandler(tornado.web.RequestHandler):
    def get(self):
        rc = {}
        rc['result'] = 'error'
        rc['info'] = 'please use Post Methods!'
        self.set_header("Content-Type", "text/plain")
        self.write(rc)

    def post(self):
        self.set_header("Content-Type", "text/plain")
        data = tornado.escape.json_decode(self.request.body)

        result = set_resource_info(data)
        if result == True:
            print 'true'
            rc = {}
            rc['result'] = 'ok'
            rc['info'] = ''
            self.write(rc)
        else:
            rc = {}
            rc['result'] = 'error'
            rc['info'] = str(result)
            self.write(rc)

class LivingSHandler(tornado.web.RequestHandler):
    def get(self):
        rc = {}
        url = self.get_argument('url', 'nothing')
        print url
        try:
            living_info = client.factory.create('ns0:LivingInfo')
            living_list = client.service.Living()['message']['LivingList'][0]
            print living_list

            for i in range(0,len(living_list)):
                if i==0: #默认只开启一路直播
                    if hasattr(living_list[i], 'Rtmp_fms'):
                        living_list[i]['Rtmp']['ServerName'] = url
                    if hasattr(living_list[i], 'LivingType'):
                        living_list[i]['LivingType'] = 'RTMP'
                living = client.factory.create('ns0:Living')
                living = living_list[i]
                living_info.LivingList[0].append(living)

            client.service.LivingS(living_info)

            rc['result'] = 'ok'
            rc['info'] = ''
        except Exception as error:
            rc['result'] = 'error'
            rc['info'] = str(error)

        self.write(rc)

_ioloop = None # 用于支持外面的结束 ...

class InternalHandler(RequestHandler):
    def get(self):
        rc = {}
        rc['result'] = 'ok'
        rc['info'] = ''

        command = self.get_argument('command', 'nothing')
        if command == 'exit':
            self.set_header('Content-Type', 'application/json')
            rc['info'] = 'exit!!!!'
            self.write(rc)
            print '_____-------'
            _ioloop_card.stop()
        elif command == 'version':
            self.set_header('Content-Type', 'application/json')
            rc['info'] = 'now version not supported!'
            rc['result'] = 'err'
            self.write(rc)


def livingS(url):
    global client
    rc = {}
    try:
        living_info = client.factory.create('ns0:LivingInfo')
        living_list = client.service.LivingD()['message']['LivingList'][0]
        living_info['IsStartFilmLiving'] = 'True'
        living_info['IsSynRecord'] = 'False'

        #print client.service.Living()['message']

        url = url[7:]
        ip = url.split(':')[0]
        url = url[len(ip)+1:]
        port = url.split('/')[0]
        url =url[len(port)+1:]
        app = url.split('/')[0]
        url = url[len(app)+1:]
        stream_id = url[:]


        for i in range(0,len(living_list)):
            if i==0: #默认只开启一路直播
                if hasattr(living_list[i],'IsUse'):
                    living_list[i]['IsUse'] = 'True'
                if hasattr(living_list[i], 'Rtmp_fms'):
                    living_list[i]['Rtmp_fms']['NetPort'] = port
                    living_list[i]['Rtmp_fms']['ServicIp'] = ip
                    living_list[i]['Rtmp_fms']['App'] = app
                    living_list[i]['Rtmp_fms']['StreamId'] = stream_id
                if hasattr(living_list[i], 'LivingType'):
                    living_list[i]['LivingType'] = 'RTMPtoFMS'
                if hasattr(living_list[i],'Rtmp'):
                    living_list[i]['Rtmp']['ServerName'] = 'None'
                living = client.factory.create('ns0:Living')
                living = living_list[i]
                living_info.LivingList[0].append(living)
            else:
                if hasattr(living_list[i],'IsUse'):
                    living_list[i]['IsUse'] = 'True'
                if hasattr(living_list[i], 'Rtmp_fms'):
                    living_list[i]['Rtmp_fms']['ServicIp'] = '  '
                    living_list[i]['Rtmp_fms']['StreamId'] = '  '
                if hasattr(living_list[i],'Rtmp'):
                    living_list[i]['Rtmp']['ServerName'] = 'None'
                living = client.factory.create('ns0:Living')
                living = living_list[i]
                living_info.LivingList[0].append(living)

        client.service.LivingS(living_info)

        rc['result'] = 'ok'
        rc['info'] = ''
    except Exception as error:
        rc['result'] = 'error'
        rc['info'] = str(error)

	return rc

def ReslivingS(ip,port,app):
    rc = {}
    rc['resulr'] = 'ok'
    rc['info'] = ''
    try:
        res_living_info_d = client.service.ResLivingInfoD()['message']
        res_living_info_d['App'] = app
        res_living_info_d['ResServerIP'] = ip
        res_living_info_d['ResServerPort'] = port
        if hasattr(res_living_info_d,'IsStartResLiving'):
            res_living_info_d['IsStartResLiving'] = 'True'
        if hasattr(res_living_info_d,'IsStartRtmpLiving'):
            res_living_info_d['IsStartRtmpLiving'] = 'True'
        client.service.ResLivingInfoS(res_living_info_d)
    except Exception as err:
        rc['result'] = 'error'
        rc['info'] = str(err)
    return rc


def start_card_server():
    global client
    wsdl_url = 'http://127.0.0.1:8086/UIServices?WSDL' 
    try:
        client = Client(wsdl_url)
    except:
        print 'wsdl_url is disable!'

if __name__ == "__main__":
    start_card_server()
