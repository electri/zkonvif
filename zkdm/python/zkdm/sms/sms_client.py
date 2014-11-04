import urllib2

help_File = urllib2.open('http://172.16.1.14:10009/sms/help')
ptz_startFile = urllib2.open('http://172.16.1.14:10009/sms/ptz/start')
ptz_startRet = ptz_startFile.read(100)
record_startFile = urllib2.open('http://172.16.1.14:10009/sms/record')
record_startRet = record_startFile.read(100) 

#FIXME sleep time
sleep(1000)

ptz_closeFile = urllib2.open('http://172.16.1.14:10009/sms/ptz/close')
ptz_closeRet = ptz_closeFile.read(100)


sleep(1000)

