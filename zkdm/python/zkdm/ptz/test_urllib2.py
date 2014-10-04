import urllib2
f = urllib2.urlopen('http://172.16.1.14:10003/ptz/student/get_pos')
print f
print f.read()
