# coding: utf-8
# @file: uty_token.py
# @date: 2014-12-24
# @brief:
# @detail: 用于描述需要注册的主机，服务信息，并提供“被代理”主机/服务的查询
#
#################################################################

import os, json, io

TOKEN_FNAME = "tokens.json"

def __valid_host(h):
    ''' 必须存在 mac, ip, hosttype '''
    if 'mac' in h and 'ip' in h and 'hosttype' in h:
        return True
    else:
        return False

def __load(fname = None):
    if fname is None:
        fname = TOKEN_FNAME

    f = io.open(fname, encoding='utf-8')
    j = json.loads(f.read())
    f.close()
    return j


def gather_hds(fname = None):
    ''' 根据 tokens.json 文件收集并构建 host description list '''
    j = __load(fname)
    hds = []
    for i in j:
        h = j[i]
        if __valid_host(h):
            hd = {}
            hd['mac'] = h['mac']
            hd['ip'] = h['ip']
            hd['type'] = h['hosttype']
            hds.append(hd)
    return hds

def gather_sds(fname = None):
    ''' 收集所有服务信息，并构建 service description list '''
    j = __load(fname)
    sds = []
    for i in j:
        h = j[i]  # host
        if __valid_host(h) and 'services' in h:
            for sk in h['services']:
                st = h['services'][sk] # type
                for sid in st:
                    s = st[sid]    # id
                    sd = {}
                    if 'url' in s:
                        sd['id'] = sid
                        sd['mac'] = h['mac']
                        sd['ip'] = h['ip']
                        sd['url'] = s['url']
                        sds.append(sd)
    return sds


if __name__ == '__main__':
    import reght, time

    hds = gather_hds()
    rh = reght.RegHost(hds)  # 主机注册

    sds = gather_sds()
    rs = reght.RegHt(sds)  # 服务注册

    time.sleep(600)


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

