@if not exist C:\Python27\python.exe (
	@echo install 
	@python-2.7.8.msi  
)
@echo cover c:\Python27

@xcopy .\Lib c:\Python27\Lib /EY
@echo copy .\zkdm to c:\zkdm


@if not exist c:\zkdm (mkdir c:\zkdm)



@if exist c:\zkdm\ptz\teacher.config (copy c:\zkdm\ptz\teacher.config .\zkdm\ptz\teacher.config /Y)


@if exist c:\zkdm\ptz\student.config (copy c:\zkdm\ptz\student.config .\zkdm\ptz\student.config /Y)


@xcopy .\zkdm c:\zkdm /EY

@if exist c:\Windows\SysWOW64 (xcopy .\SysWOW64 c:\Windows\SysWOW64 /EY)
@c:

@cd c:\zkdm\ptz
@echo please alter teacher.config about ptz
@notepad teacher.config

@echo please alter student.config about ptz
@notepad student.config

@echo please alter bd.config about ptz
@notepad bd.config
@echo off
@install_ptz_winservice.bat
