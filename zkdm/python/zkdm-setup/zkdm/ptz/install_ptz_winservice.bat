@echo on

@c:\Python27\python PtzWinService.py install

@
sc config zonekey.service.ptz start= auto


@sc start zonekey.service.ptz
@echo 成功安装 zonekey.service.ptz 服务
@echo off

pause