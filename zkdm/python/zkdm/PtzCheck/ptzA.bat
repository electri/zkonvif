@echo on
@echo 检测云台是否接错端口号
@echo.
@echo 输入被云台名称(譬如 student,teacher...)
@set /p ptz_name= 
@curl "http://127.0.0.1:10003/ptz/%ptz_name%/set_pos?x=0&y=0"

ping -n 3 127.0.0.1>nul

@curl "http://127.0.0.1:10003/ptz/%ptz_name%/set_pos?x=400&y=400"

ping -n 3 127.0.0.1>nul

@curl "http://127.0.0.1:10003/ptz/%ptz_name%/set_pos?x=-400&y=-400"

ping -n 3 127.0.0.1>nul

@curl "http://127.0.0.1:10003/ptz/%ptz_name%/set_pos?x=0&y=0"
@echo.
@echo.
@echo.
@echo off
@pause