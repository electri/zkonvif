# coding: utf-8

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import socket

from tornado.options import define, options
from tornado.web import RequestHandler, Application, url
from RecordingCommand import RecordingCommand

define("port", default=8888, help="run on the given port", type=int)

def _param(req, key):
	if key in req.request.arguments:
		return req.request.arguments
	else:
		return None

_rcmd = None

class MainHandler(tornado.web.RequestHandler):
	def get(self):
		self.write("Use the /recording/help for more help !")

class HelpHandler(tornado.web.RequestHandler):
	def get(self):
		self.render('help.html')

class CmdHandler(tornado.web.RequestHandler):
	def get(self):
		rc={}
		rc['result']='ok'
		rc['info']=''

		cmd = _param(self, 'RecordCmd')

		if cmd is None:
			rc['result'] = 'err'
			rc['info'] = '"RecordCmd" MUST be supplied!'
			self.write(rc)
			return
		elif cmd['RecordCmd'] == ['StartRecord']:
			rc=_rcmd.start()
			self.write(rc)

		elif cmd['RecordCmd']==['PauseRecord']:
			rc=_rcmd.pause()
			self.write(rc)

		elif  cmd['RecordCmd']==['StopRecord']:
			rc=_rcmd.stop()
			self.write(rc)

		elif cmd['RecordCmd']==['ResumeRecord']:
			rc=_rcmd.resume()
			self.write(rc)

		elif cmd['RecordCmd']==['OpenPicFile']:
			self.write(rc)

		elif cmd['RecordCmd']==['PlayPicFile']:
			self.write(rc)

		elif cmd['RecordCmd']==['StopPicFile']:
			self.write(rc)

		elif cmd['RecordCmd']==['OpenVideoFile']:
			self.write(rc)

		elif cmd['RecordCmd']==['OpenVideoFile']:
			self.write(rc)

		elif cmd['RecordCmd']==['ChangeCard']:
			self.write(rc)

		elif cmd['RecordCmd']==['StopVideoFile']:
			self.write(rc)

		elif cmd['RecordCmd']==['SetRecordMode']:
			self.write(rc)

		elif cmd['RecordCmd']==['SetFileProperty']:
			self.write(rc)

		elif cmd['RecordCmd']==['SetFileProperty']:
			self.write(rc)

		elif cmd['RecordCmd']==['SetCourseInfo']:
			self.write(rc)

		elif cmd['RecordCmd']==['SetResRecordEnable']:
			self.write(rc)

		elif cmd['RecordCmd']==['SetVolume']:
			self.write(rc)

		elif cmd['RecordCmd']==['SetFilmParams']:
			self.write(rc)

		elif cmd['RecordCmd']==['SetResParams']:
			self.write(rc)

		elif cmd['RecordCmd']==['SetDisSolve']:
			self.write(rc)

		elif cmd['RecordCmd']==['SetCardInfo']:
			self.write(rc)

		elif cmd['RecordCmd']==['ChangeCard']:
			self.write(rc)

		elif cmd['RecordCmd']==['SetCardEffect']:
			self.write(rc)

		elif cmd['RecordCmd']==['SetAllEffect']:
			self.write(rc)

		elif cmd['RecordCmd']==['SetPicInPicCardPort']:
			self.write(rc)

		elif cmd['RecordCmd']==['SetPicInPicMode']:
			self.write(rc)

		elif cmd['RecordCmd']==['ChangePicInPic']:
			self.write(rc)

		elif cmd['RecordCmd']==['SetPositionAndSize']:
			self.write(rc)

		elif cmd['RecordCmd']==['ClosePicInPic']:
			self.write(rc)

		elif cmd['RecordCmd']==['SetCaption']:
			self.write(rc)

		elif cmd['RecordCmd']==['CaptionClose']:
			self.write(rc)

		elif cmd['RecordCmd']==['SetLogo']:
			self.write(rc)

		elif cmd['RecordCmd']==['LogoClose']:
			self.write(rc)

		elif cmd['RecordCmd']==['ManualTrace']:
			self.write(rc)

		elif cmd['RecordCmd']==['AutoTrace']:
			self.write(rc)

		elif cmd['RecordCmd']==['MouseTrace']:
			self.write(rc)

		elif cmd['RecordCmd']==['Zoom']:
			self.write(rc)

		elif cmd['RecordCmd']==['QueryRAllInfo']:
			self.write(rc)

		elif cmd['RecordCmd']==['FtpUrl']:
			rc['info']='ftp url!'
			self.write(rc)

		else:
			print cmd
			print cmd['StartTime']
			print cmd['RecordCmd']
			rc['result'] = 'err'
			rc['info'] = 'command not Support!'
			self.write(rc)
		return


def main():

	tornado.options.parse_command_line()
	application = tornado.web.Application([
        url(r"/", MainHandler),
        url(r"/recording/cmd",CmdHandler),
		url(r"/recording/help", HelpHandler),
    ])

	global _rcmd
	_rcmd = RecordingCommand()

	application.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
