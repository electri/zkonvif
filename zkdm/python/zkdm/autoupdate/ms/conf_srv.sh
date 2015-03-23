#!/bin/bash

# 此脚本检查 conf_srv.py 是否在运行，如果没有运行，则启动

# TODO: 侯工，修改这个path，使之指向 conf_srv.py 的完整路径
APP="/<full path>/conf_srv.py"

pgrep conf_srv.py
if [ "$?" -eq "0" ]
then
	echo 'running'
	exit
else
	$APP &
fi

