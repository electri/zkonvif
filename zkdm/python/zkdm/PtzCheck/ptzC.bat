@echo on
@echo 检测主机,云台双向通讯
@echo.
@echo 输入被云台名称(譬如 student,teacher...)
@set /p ptz_name= 
@curl http://127.0.0.1:10003/ptz/%ptz_name%/is_prepared
@echo.
@echo.
@echo.
@echo off
@pause
