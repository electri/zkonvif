# coding: utf-8
# 本地配置 ...


import json, io 


def load_config(fname):
    ''' 加载配置，使用 json 格式 '''
    f = io.open(fname, 'r', encoding='utf-8')
    data = json.load(f)
    f.close()
    return data


def save_config(fname, data):
    ''' 将 dict 序列化保存 '''
    f = io.open(fname, 'w', encoding='utf-8')
    f.write(unicode(json.dumps(data, ensure_ascii = False)))
    f.close()

        

if __name__ == '__main__':
    from pprint import pprint
    data = load_config('config.json')
    print(type(data))
    pprint(data)
    data['services'][0]['enable'] = False
    save_config('config.json.session', data)
