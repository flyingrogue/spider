# -*- coding:utf-8 -*-


import requests
import json
import re

url='https://xueqiu.com/stock/cata/stocklist.json?page={}&size=30&order=desc&orderby=percent&type=30&isdelay=1&_=1545557201182'
headers={
    'X-Requested-With':'XMLHttpRequest',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
    'Cookie':'xq_a_token=663059f1a494115c0dfac8bc11acf01c72ca2407;'
}
item=[]
# for page in range(1,98):
#     res=requests.get(url.format(page),headers=headers)
#     results=json.loads(res.text)['stocks']
#     for result in results:
#         item.append(result['name']+result['symbol'])
# print(len(item))
# f=open('stockcode_hk.txt','w',encoding='utf8')
# f.write(str(item))

# f=open('stockcode_hk.txt','r',encoding='utf8')
# items=eval(f.read())
# count=0
# for item in items:
#     if re.match('.*?[08]\d{4}$',item,re.S):
#         count+=1
#     else:
#         print(item)
# print(count)

