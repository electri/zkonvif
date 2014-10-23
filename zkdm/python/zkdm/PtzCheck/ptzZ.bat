@echo on
@echo 检测云台倍数获取
@echo.
@echo 输入被云台名称(譬如 student,teacher...)
@set /p ptz_name= 
@echo 设置云台倍数(譬如 1000)
@set /p zoom= 
@curl http://127.0.0.1:10003/ptz/%ptz_name%/set_zoom?%p_zoom%
@curl http://127.0.0.1:10003/ptz/%ptz_name%/get_zoom
@echo.
@echo.
@echo.
@echo off
@pause
