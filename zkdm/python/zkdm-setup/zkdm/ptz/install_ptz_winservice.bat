@echo on
@echo 安装 zonekey.service.ptz 服务
c:\Python27\python PtzWinService.py install


@echo 设置 zonekey.service.ptz 为自动启动
sc config zonekey.service.ptz start= auto

@echo.
@echo.
@echo.
@echo **********************************************************************
@echo *                       注意事项                                      *
@echo * 在windows services中,查看 zonekey.service.ptz 是否存在? 若存在:     *
@echo *   1  在c:\zkdm\ptz目录下,修改配置文件teacher.config和student.config *
@echo *   (hva,vva分别为水平视角,垂直视角,以度为单位)                       *
@echo *   2 启动 zonekey.service.ptz  服务                                  *
@echo **********************************************************************
@echo.
@echo off
pause



