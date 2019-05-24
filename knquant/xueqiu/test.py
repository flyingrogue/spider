
import requests
import json
import re
from urllib.parse import unquote
import time
# headers={
#         'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
#         'Host':'yield.chinabond.com.cn',
#         'Origin':'http://yield.chinabond.com.cn',
#         'X-Requested-With':'XMLHttpRequest',
#         'Referer':'http://yield.chinabond.com.cn/cbweb-mn/yield_main',
#         #'Cookie':'JSESSIONID=0000P6Cf0-Ufk8X4DDVpDeSa10h:-1',
#     }
#url='http://yield.chinabond.com.cn/cbweb-mn/yc/ycDetail?ycDefIds=2c9081e50a2f9606010a3068cae70001&&zblx=txy&&workTime=2018-09-20&&dxbj=0&&qxlx=0,&&yqqxN=N&&yqqxK=K&&wrjxCBFlag=0&&locale=zh_CN'


#a='%E9%A6%99%E6%B8%AF%E4%B9%9D%E9%BE%99%E5%B9%BF%E4%B8%9C%E9%81%9330%E5%8F%B7%E6%96%B0%E6%B8%AF%E4%B8%AD%E5%BF%83%E7%AC%AC%E4%BA%8C%E5%BA%A717%E6%A5%BC'
#a=unquote(a)
#print(a)


url='https://xueqiu.com/statuses/search.json?count=10&comment=0&symbol=SZ002395&hl=0&source=user&sort=time&page=10&q='
url2='https://xueqiu.com/v4/statuses/user_timeline.json?page=204&user_id=1817409357'
headers={
        'X-Requested-With': 'XMLHttpRequest',
        #'Referer': 'https://xueqiu.com/u/1587243856',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
        #'Cookie': 'xq_a_token=a5009edf282c45bd2c24c7997db8ff14e29e1fa4;',
                              }
cookies=['c906a480552717666c3e3ec4bc0d0fc57309e471','37fc1735d21daea9d4e775b190bda674b8af74ac','243bb1cce89c8d4d365a26452e50d6e62b83db37',
         'e41ec0d9001db0743e4770e112a39c92652b4cd4','71c5cbb7171116b22c6f91b404d2cfa61d656a6d','0c090c0bc6311907a205b3aad0084e4df078a4d8',
         ]

for cookie in cookies:
    headers['Cookie']='xq_a_token={};'.format(cookie)
    res=requests.get(url,headers=headers)
    print(res.text,res.status_code)
    #if re.match('^{"count".*}$', res.text, re.S):

    result = json.loads(res.text)
    statuses = result.get('list')
    if statuses:
        status_item = {}
        for status in statuses:
            status_item['user'] = status.get('user').get('screen_name')
            status_item['created_time'] = status.get('created_at')
            status_item['article_id'] = status.get('id')
            status_item['article'] = status.get('text')
            status_item['retweet_count'] = status.get('retweet_count')
            status_item['reply_count'] = status.get('reply_count')
            status_item['fav_count'] = status.get('like_count')
            #print(status_item)























