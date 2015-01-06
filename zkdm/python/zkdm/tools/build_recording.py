# coding: utf-8
# @file: build_recording.py
# @date: 2014-12-25
# @brief:
# @detail: 用于生成 recording 服务描述
#
#################################################################


def build(desc, var):
    ''' desc 来自 template.json 的 recording 服务的描述，根据此描述，
        生成 
         {
             "CARD01": {
                 "url": "...",
                 "private": {
                     ....
                 }
             }，
         } 之类的描述 '''
    ssd = {}

    # 目前仅仅处理一个 id 的情况
    if 'id' in desc and 'urlfmt' in desc:
        idd = {}
        # 使用 url 中的变量替换
        url = desc['urlfmt']
        idd['url'] = url.replace("$token", var['token'], 1)
        idd['private'] = {}
        target_ip = desc['private']['target_ip']
        idd['private']['target_ip'] = target_ip.replace("$ip", var['ip'], 1)
        idd['private']['target_port'] = desc['private']['target_port']

        ssd[desc['id']] = idd

    return ssd



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

