@echo on
@echo 安装python 2.7.8

@python-2.7.8.msi

@echo 覆盖 c:\Python27

@xcopy .\Python27 c:\Python27 /EY

@echo 拷贝 .\zkdm 到 c:\zkdm


@if not exist c:\zkdm (mkdir c:\zkdm)



@if exist c:\zkdm\ptz\teacher.config (copy c:\zkdm\ptz\teacher.config .\zkdm\ptz\teacher.config /Y)


@if exist c:\zkdm\ptz\student.config (copy c:\zkdm\ptz\student.config .\zkdm\ptz\student.config /Y)


@if exist c:\zkdm\ptz\bd.config (copy c:\zkdm\ptz\bd.config .\zkdm\ptz\bd.config /Y)


@if exist c:\zkdm\host\config.json (copy c:\zkdm\host\config.json .\zkdm\host\config.json /Y)
@xcopy .\zkdm c:\zkdm /EY

@if exist c:\Windows\SysWOW64 (xcopy .\SysWOW64 c:\Windows\SysWOW64 /EY copy .\System64\curl.exe c:\Windows\System32 /Y)
@echo 安装pythonwin32
@pywin32-218.win32-py2.7.exe

@c:

@cd c:\zkdm\ptz
@echo 请修改教师的配置文件
@notepad teacher.config

@echo 请修改学生的配置文件
@notepad student.config

@echo 请修改板书配置
@notepad bd.config
@cd c:\zkdm\host
@echo 请修改主机类型,注册服务器参数
@notepad config.json
@echo off
@cd c:\zkdm\dm
@install_dm_winservice.bat
