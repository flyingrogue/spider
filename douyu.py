# -*- coding:utf-8 -*-

import requests
import json
from lxml import etree

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
    'X-Requested-With':'XMLHttpRequest',
    #'Cookie':'dy_did=0e1ed9145f2d43747d8259f800081501',
}
url = 'https://www.douyu.com/gapi/rkc/directory/0_0/{page}'

def get_item(page):
    res = requests.get(url.format(page=page),headers=headers)
    print(res.text)
    datas = json.loads(res.text)['data']['rl']
    count = 0
    for data in datas:
        item = {}
        item['name'] = data['nn']
        item['title'] = data['rn']
        item['type'] = data['c2name']
        item['hot'] = data['ol']
        item['tag'] = data['od']
        item['id'] = data['rid']
        item['cover'] = data['rs1']
        print(item)
        count += 1
    return count



if __name__=='__main__':
    scount = 0
    for page in range(1,101):
        count = get_item(page)
        scount += count
    print(scount)

