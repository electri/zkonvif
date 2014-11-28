@echo on

@c:\Python27\python DMWinService.py install

@sc config zonekey.service.dm start= auto
@sc start zonekey.service.dm
@echo zonekey.service.dm succeed and running ...
@echo off

pause