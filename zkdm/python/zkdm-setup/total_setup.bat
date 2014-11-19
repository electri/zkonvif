@echo on
@echo install python 2.7.8

@python-2.7.8.msi

@echo install pythonwin32
@pywin32-218.win32-py2.7.exe
@echo cover c:\Python27\Lib\s
@xcopy .\Lib c:\Python27\Lib /EY




@echo copy .\zkdm to c:\zkdm


@if not exist c:\zkdm (mkdir c:\zkdm)



@if exist c:\zkdm\ptz\teacher.config (copy c:\zkdm\ptz\teacher.config .\zkdm\ptz\teacher.config /Y)


@if exist c:\zkdm\ptz\student.config (copy c:\zkdm\ptz\student.config .\zkdm\ptz\student.config /Y)


@if exist c:\zkdm\ptz\bd.config (copy c:\zkdm\ptz\bd.config .\zkdm\ptz\bd.config /Y)


@if exist c:\zkdm\host\config.json (copy c:\zkdm\host\config.json .\zkdm\host\config.json /Y)
@xcopy .\zkdm c:\zkdm /EY

@if exist c:\Windows\SysWOW64 (xcopy .\SysWOW64 c:\Windows\SysWOW64 /EY copy .\System64\curl.exe c:\Windows\System32 /Y)
@c:

@cd c:\zkdm\ptz
@echo please alter teacher.config
@notepad teacher.config

@echo please alter student.config
@notepad student.config

@echo please alter bd
@notepad bd.config
@cd c:\zkdm\host

@echo please alter host type and reg service parameters
@notepad config.json
@echo off
@cd c:\zkdm\dm
@install_dm_winservice.bat
