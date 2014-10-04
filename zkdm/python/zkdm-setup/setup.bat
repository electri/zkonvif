@echo on
@echo now setup python 2.7.8
python-2.7.8.msi

@echo now cover c:\Python27
xcopy .\Python27 c:\Python27 /EY

@echo copy .\zkdm to c:\zkdm
mkdir c:\zkdm
xcopy .\zkdm c:\zkdm /EY

@echo now setup pywin32
pywin32-218.win32-py2.7.exe

@echo now,we must set envirenment:

@echo if you setup in default
@echo 	path=c:\Python27\


@echo now we best restart computer
@echo ctrl + break then exit
@echo off



