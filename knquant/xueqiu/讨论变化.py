

import requests
import json


headers={
        'X-Requested-With':'XMLHttpRequest',
        'Referer':'https://xueqiu.com/hq/screener',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
        'Cookie':'xq_a_token=e308965436e56ce7e18483bad51498ef582a0624; xq_r_token=335505f8d6608a9d9fa932c981d547ad9336e2b5',
}

# url='https://xueqiu.com/stock/screener/screen.json?category=SH&exchange=&areacode=&indcode=&orderby=symbol&order=desc&current=ALL&pct=ALL&' \
#     'page={}&follow=87_954676&follow7d=0_5365&tweet=12_207930&tweet7d=0_2691&_=1543502331464'
url='https://xueqiu.com/stock/screener/screen.json?category=SH&exchange=&areacode=&indcode=&orderby=symbol&order=desc&current=ALL&pct=ALL&' \
    'page={}&follow=87_956021&follow7d=0_4073&tweet=12_214438&tweet7d=0_3470&deal=0_3203&deal7d=0_21&_=1544580184608'
data=[]
# for page in range(1,121):
#         res=requests.get(url.format(page),headers=headers)
#         results=json.loads(res.text).get('list')
#         print(page)
#         for result in results:
#                 item={}
#                 item['symbol']=result.get('symbol')
#                 item['name'] = result.get('name')
#                 item['follow']=result.get('follow')
#                 item['follow7d'] = result.get('follow7d')
#                 item['tweet'] = result.get('tweet')
#                 item['tweet7d'] = result.get('tweet7d')
#                 item['deal']=result.get('deal')
#                 item['deal7d']=result.get('deal7d')
#                 print(item)
#                 data.append(item)
# f=open('data_new.txt','w',encoding='utf8')
# f.write(str(data))

# f=open('data_old.txt','r',encoding='utf8')
# items=eval(f.read())
# follow=0
# follow7d=0
# tweet=0
# tweet7d=0
# for item in items:
#         follow+=dict(item)['follow']
#         follow7d+=dict(item)['follow7d']
#         tweet+=dict(item)['tweet']
#         tweet7d+=dict(item)['tweet7d']
# print(follow,follow7d,tweet,tweet7d)


f=open('data_old.txt','r',encoding='utf8')
old=eval(f.read())
f1=open('data_new.txt','r',encoding='utf8')
new=eval(f1.read())
count=0
for i in old:
    for j in new:
        if j['symbol']==i['symbol']:
            cha=dict(i)['tweet']+dict(j)['tweet7d']-dict(j)['tweet']
            if cha>=0:
                count+=1
                print(dict(i)['name'],cha)
            break
print(count)