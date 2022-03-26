import requests

def getnow(leader_uid):
    true=True
    r = eval(requests.get(
        'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?visitor_uid=2&host_uid={}'.format(leader_uid)).text)
    print('https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?visitor_uid=2&host_uid={}'.format(leader_uid))
    return r['data']['cards'][0]['desc']['dynamic_id']

def getcontext(leader_uid):
    r = eval(requests.get(
        'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?visitor_uid=2&host_uid={}'.format(leader_uid)).text)
    null=None
    false=False
    true=True
    text=eval(r['data']['cards'][0]['card'])

    if 'item' in text:
        text=text['item']
        if 'category' in text:
            return ["图片",text['description']]
        elif 'content' in text:
            return ["动态",text['content']]
    elif 'title' in text:
        return ["视频", text['title']]

if __name__ == '__main__':
    print(getcontext())