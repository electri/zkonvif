#!/bin/bash

# 生成 target_info 文件

mac=`cat /sys/class/net/eth0/address | sed s/://g`
hosttype='ubuntu test'

# 写入 mac + hosttype 
echo "mac=${mac}" > info
echo "hosttype=${hosttype}" >> info

# 第一个服务
echo "stype=log" >> info
echo "id=0" >> info
echo "private=url:/log/query" >> info

# 更多的服务 ...


# 启动 pong
./pong -f info

