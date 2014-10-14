@echo on
@echo 安装 python 2.7.8
python-2.7.8.msi
@echo 覆盖 c:\Python27
xcopy .\Python27 c:\Python27 /EY
@echo 拷贝 .\zkdm 到 c:\zkdm

if not exist c:\zkdm (mkdir c:\zkdm)

if exist c:\zkdm\ptz\teacher.config (copy c:\zkdm\ptz\teacher.config .\zkdm\ptz\teacher.config /Y)
if exist c:\zkdm\ptz\student.config (copy c:\zkdm\ptz\teacher.config .\zkdm\ptz\student.config /Y)

xcopy .\zkdm c:\zkdm /EY
if %processor_architecture% ==x86 (xcopy .\SysWOW32 c:\Windows\SysWOW32 /EY) else xcopy .\SysWOM64 c:\Windows\SysWOW64 /EY 

else 
@echo 安装 pywin32
pywin32-218.win32-py2.7.exe
@echo off
cd  c:\zkdm\ptz
install_ptz_winservice.bat
