@echo on
vcredist_x86.exe
@echo install python 2.7.8

@python-2.7.8.msi

@echo install pythonwin32
@pywin32-218.win32-py2.7.exe
@echo cover c:\Python27\Lib\s
@xcopy .\Lib c:\Python27\Lib /EY




@echo copy .\zkdm to c:\zkdm


@if not exist c:\zkdm (mkdir c:\zkdm)



@if exist c:\zkdm\ptz\card0.config (copy c:\zkdm\ptz\card0.config .\zkdm\ptz\card0.config /Y)


@if exist c:\zkdm\ptz\card2.config (copy c:\zkdm\ptz\card2.config .\zkdm\ptz\card2.config /Y)


@if exist c:\zkdm\ptz\card5.config (copy c:\zkdm\ptz\card5.config .\zkdm\ptz\card5.config /Y)


@if exist c:\zkdm\host\config.json (copy c:\zkdm\host\config.json .\zkdm\host\config.json /Y)
@if exist c:\zkdm\dm\config.json (copy c:\zkdm\dm\config.json .\zkdm\dm\config.json /Y)
@xcopy .\zkdm c:\zkdm /EY
@c:

@cd c:\zkdm\ptz
@echo please alter teacher.config
@notepad card0.config

@echo please alter student.config
@notepad card2.config

@echo please alter bd
@notepad card5.config
@cd c:\zkdm\host

@echo please alter host type and reg service parameters
@notepad config.json
@echo off
@cd c:\zkdm\dm
@install_dm_winservice.bat
