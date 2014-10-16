@echo on
c:\Python27\python PtzWinService.py install

sc config zonekey.service.ptz start= auto

sc start zonekey.service.ptz

@echo zonekey.service.ptz 成功安装并运行
@echo off
pause