# coding: utf-8
# @file: build_ptz.py
# @date: 2014-12-25
# @brief:
# @detail:
#
#################################################################

def build(desc, var):
    ssd = {}
    if 'count' in desc and 'idfmt' in desc and 'urlfmt' in desc and 'private' in desc:
        n = desc['count']
        for i in range(1, n+1):  # 注意，从 1 开始
            idd = {}
            idfmt = desc['idfmt']
            idk = idfmt % (i)
            
            urlfmt = desc['urlfmt']
            url = urlfmt.replace('$id', idk, 1)
            idd['url'] = url.replace('$token', var['token'], 1)

            idd['private'] = {}
            idd['private']['arm_ip'] = desc['private']['arm_ip'].replace('$ip', var['ip'], 1)
            idd['private']['arm_port'] = desc['private']['arm_port']
            idd['private']['others'] = desc['private']['others']
            
            ssd[idk] = idd

    return ssd




# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

