
import requests
from requests.exceptions import ProxyError
from urllib3.exceptions import MaxRetryError
from requests import session
import json
import time
import re

proxyHost = "http-dyn.abuyun.com"
proxyPort = "9020"
proxyUser = "HP7Y01400L962MUD"
proxyPass = "ED8926D78920DD44"


base_url='https://xueqiu.com/'
url='https://xueqiu.com/statuses/search.json?count=10&comment=0&symbol=SH601318&hl=0&source=user&sort=time&page={}&q='
url2 = 'https://xueqiu.com/stock/screener/screen.json?category=SH&exchange=&areacode=&indcode=&orderby=symbol&order=desc&current=ALL&pct=ALL&' \
              'page={}&follow=87_956021&follow7d=0_4073&tweet=12_214438&tweet7d=0_3470&deal=0_3203&deal7d=0_21'
headers={
    #'Host':'xueqiu.com',
    #'Referer': 'https://xueqiu.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
}
headers2={
    'Host':'xueqiu.com',
    'X-Requested-With': 'XMLHttpRequest',
    #'Referer': 'https://xueqiu.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
    'Cookie': 'xq_a_token=243bb1cce89c8d4d365a26452e50d6e62b83db37;',
}
proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
        "host": proxyHost,
        "port": proxyPort,
        "user": proxyUser,
        "pass": proxyPass,
    }
proxies = {
        "http": proxyMeta,
        "https": proxyMeta,
    }

a=time.time()
for page in range(1,101):
    res=None
    while True:
        try:
            #sess=session()
            #first=sess.get(base_url,headers=headers,proxies=proxies,timeout=3)
            res=requests.get(url.format(page),headers=headers2,proxies=proxies,timeout=3)
        except (OSError,MaxRetryError,ProxyError) as e:
            print(e)
        if res and re.match('{.*}',res.text,re.S):
            print(res.text)
            break
b=time.time()
print(b-a)




    #sess.close()



# result = json.loads(res.text)
# statuses = result.get('list')
# if statuses:
#     status_item = {}
#     for status in statuses:
#         status_item['user'] = status.get('user').get('screen_name')
#         status_item['created_time'] = status.get('created_at')
#         status_item['article_id'] = status.get('id')
#         status_item['article'] = status.get('text')
#         status_item['retweet_count'] = status.get('retweet_count')
#         status_item['reply_count'] = status.get('reply_count')
#         status_item['fav_count'] = status.get('like_count')

