from datetime import datetime
import time

from PtzWrap import PtzWrap

Ptz = PtzWrap()
Ptz.open('COM4', 1)
time.sleep(5.0)
Ptz.call("left", {'speed':[2]})
time.sleep(5.0)
Ptz.stop()
Ptz.close()
