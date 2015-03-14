#!/usr/bin/python
# coding: utf-8
#
# @file: uty_au.py
# @date: 2015-03-10
# @brief:
# @detail: 一组方便 au 的函数
#
#################################################################


import platform

_uname = platform.uname()
_windows = (_uname[0] == 'Windows')

vm_macs = [
    '005056', # vmware prefix
    '00163e', # xen
    '080027', # vbox
    ]


def __is_vm(m):
    for i in vm_macs:
        if m[:6] == i:
            return True
    return False


def get_mac_ip():
    ''' 返回本机首选mac地址和首选ip地址，并且排除虚拟机 ...
    '''
    mac, ip = None, None

    if _windows:
        import wmi
        c = wmi.WMI()
        for nif in c.Win32_NetworkAdapterConfiguration(IPEnabled=1):
            m = str(nif.MACAddress)
            m = m.replace(':', '').lower()
            if not __is_vm(m):
                return m,nif.IPAddress[0]
        return None,None
    else:
        import netifaces as nif
        nic = 'eth0'
        if platform.uname()[0] == 'Darwin':
            nic = 'en0'

        for i in nif.interfaces():
            if i == nic:
                addr = nif.ifaddresses(i)
                mac = addr[nif.AF_LINK][0]['addr']
                mac = mac.replace(':', '').lower()
                ip = addr[nif.AF_INET][0]['addr']
                return mac,ip
        return None,None


def isin_mac_scope(from_mac, to_mac):
    ''' 返回本机的mac是否属于指定的地址段内 '''
    fm = from_mac.replace(':', '').lower()
    tm = to_mac.replace(':', '').lower()
    m = get_mac_ip()[0]
    if len(fm) == len(m) and len(tm) == len(m):
        if __str_cmp(fm, m) <= 0 and __str_cmp(m, tm) <= 0:
            return True
    return False


def __str_cmp(s1, s2):
    if len(s1) != len(s2):
        raise Exception('NOT eq len')

    for i in range(0, len(s1)):
        if s1[i] < s2[i]:
            return -1
        if s1[i] > s2[i]:
            return 1
    return 0


if __name__ == '__main__':
    print get_mac_ip()
    print isin_mac_scope('081196000000', '081196cdf58b')


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

