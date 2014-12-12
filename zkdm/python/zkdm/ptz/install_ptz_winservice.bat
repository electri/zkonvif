@echo on

@c:\Python27\python PtzWinService.py install

@sc config zonekey.service.ptz start= auto
@sc start zonekey.service.ptz
@echo.
@echo.
@echo zonekey.service.ptz scceed and be running ...
@ping 127.1 -n 6 >null
@echo off
