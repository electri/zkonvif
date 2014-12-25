# coding: utf-8
# @file: test_ptz.py
# @date: 2014-12-25
# @brief:
# @detail: 从名字服务，利用 listAll 得到服务列表，找出所有 ptz 服务，对其进行逐条测试
#
#################################################################


import urllib2, json, time

NSURL = 'http://172.16.1.14:8080/deviceService/listAll'
passed = 0
tested = 0

def __get_utf8_body(req):
    # FIXME: 更合理的应该是解析 Content-Type ...
    body = '';
    b = req.read().decode('utf-8')
    while b:
        body += b
        b = req.read().decode('utf-8')
    return body

def test_ptz(url):
    ''' 这里发出云台测试命令 ...'''
    print '=======', url, '==========='
    left_url = url + '/left?speed=1'
    global passed
    try:
        urllib2.urlopen(left_url)
        print '\tleft ok'
        passed += 1
    except Exception as e:
        print '\tleft fault:', left_url

    time.sleep(1.0)

    stop_url = url + '/stop'
    try:
        urllib2.urlopen(stop_url)
        print '\tstop ok'
        passed += 1
    except:
        print '\tstop fault:', stop_url

    print '============================================'


req = urllib2.urlopen(NSURL)
body = __get_utf8_body(req)

ptz_urls = []
sds = json.loads(body)
for h in sds:
    for sid in sds[h]:
        sd = sds[h][sid]
        if sd['type'] == 'ptz':
            ptz_urls.append(sd['url'])
passed = 0
tested = len(ptz_urls) * 2 # 每个云台测试两项
for url in ptz_urls:
    test_ptz(url)

print '****************************************************'
print '** TEST: %d, PASSED: %d ' % (tested, passed)
print '****************************************************'



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

