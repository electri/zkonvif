import threading, zipfile

class Asynczip(threading.Thread):
		def __init__(self, infile, outfile):
				threading,Thread.__init__(self)
				self.infile = infile
				self.outfile = outfile



		def run(self):
				f = zipfile.ZipFile(self.outfile, 'w', zipfile.ZIP_DEFAULTED)
				f.write(self.infile)
				f.close()
				print 'Finished background zip of: ', self.infile

background = AsyncZIP('mydata.txt', 'myarchive.zip')
background.start()
print 'The main program continues to run in foregound.'

background.jon() #wait for the background task to finish
print 'Main program waited until background was done.'

