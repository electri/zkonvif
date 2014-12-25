# coding: utf-8
# @file: tmplmaker.py
# @date: 2014-12-25
# @brief:
# @detail: 根据模板文件，组合入参 mac, ip, hosttype, token 生成一个主机的所有信息
#
#################################################################


import json, io, imp, os

def __build_sds(script_fname, desc, var):
    ''' script_fname 为需要加载的模块名字，desc 为这种服务的描述 '''
    mod_name, ext_name = os.path.splitext(os.path.split(script_fname)[-1])
    mod = None

    if ext_name == ".py":
        mod = imp.load_source(mod_name, script_fname)
    elif ext_name == ".pyc":
        mod = imp.load_compiled(mod_name, script_fname)

    if mod is None:
        print 'WARNING: cannot load script:', script_fname
        return {}  # XXX: 目前看起来是安全的

    if not hasattr(mod, "build"):
        print 'WARNING: the script %s is INVALID build script' % (script_fname)
        return {}

    return getattr(mod, "build")(desc, var)


def build_host(mac, ip, hosttype, token, fname = 'template.json'):
    ''' 根据fname指定的规则，生成主机描述 '''
    f = io.open(fname, encoding='utf-8')
    t = json.loads(f.read())
    f.close()

    # 基本变量
    var = { 'mac': mac, 'ip': ip, 'hosttype': hosttype, 'token': token }

    # build host: mac, ip, hosttype
    host = {}

    # FIXME: 这里本应该列举 t 的子项，但现在没有必要考虑那么复杂 ..
    host['mac'] = mac
    host['ip'] = ip
    host['hosttype'] = hosttype

    if 'services' in t:
        host['services'] = {}
        hss = host['services']

        tss = t['services']
        for tsk in tss:
            if 'comment' in tsk:
                continue    # 略过注释
            ts = tss[tsk]   # ts 为一个服务描述
            if 'script' in ts and 'desc' in ts:
                hss[tsk] = __build_sds(ts['script'], ts['desc'], var)
    return host


def build_tokens(ifname, ofname):
    ''' 输入为 mac ip 文件，输出为 tokens.json 格式文件 '''
    tokid = 1 # token id 从1开始累加
    tokens = {}
    hosttype = 'arm'    # FIXME: 这个主机类型到底如何获取更合理呢？

    f = open(ifname, "r")
    for line in f:
        line = line.strip()
        if len(line) < 5:
            continue

        # 每行使用 空格分隔 mac ip
        mac,ip = line.split(' ', 1)

        tokens[str(tokid)] = build_host(mac, ip, hosttype, str(tokid), 'template.json')
        tokid += 1
    f.close()
    
    f = open(ofname, 'w')
    f.write(json.dumps(tokens))
    f.close()


if __name__ == '__main__':
    #h = build_host("665544332211", "192.168.13.31", "arm", "1")
    #print json.dumps(h)
    build_tokens('mi.txt', 'token-tmp.json')



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

