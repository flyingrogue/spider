
import requests
import json

# headers={
#         'X-Requested-With':'XMLHttpRequest',
#         'Referer':'https://xueqiu.com/S/SH601318',
#         'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
#         'Cookie':'xq_a_token=2fb6db7c1714e3863370ace9639cbfd93152e107; xq_r_token=05a97c8a823232f481583f474e307ea153a39adc',
#         }
# url='https://xueqiu.com/statuses/search.json?count=10&comment=0&symbol=SH600028&hl=0&source=user&sort=time&page=13&q='
# res=requests.get(url,headers=headers)
# print(res.text,res.status_code)
# statuses=json.loads(res.text).get('list')
# if statuses:
#     for status in statuses:
#             status_item={}
#             status_item['user_id'] = status.get('user_id')
#             status_item['created_time'] = status.get('created_at')
#             status_item['article_id'] = status.get('id')
#             status_item['article'] = status.get('text')
#             status_item['retweet_count'] = status.get('retweet_count')
#             status_item['reply_count'] = status.get('reply_count')
#             status_item['fav_count'] = status.get('like_count')
#             print(status_item)



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
for page in range(1,121):
        res=requests.get(url.format(page),headers=headers)
        results=json.loads(res.text).get('list')
        print(page)
        for result in results:
                item={}
                item['symbol']=result.get('symbol')
                item['name'] = result.get('name')
                item['follow']=result.get('follow')
                item['follow7d'] = result.get('follow7d')
                item['tweet'] = result.get('tweet')
                item['tweet7d'] = result.get('tweet7d')
                item['deal']=result.get('deal')
                item['deal7d']=result.get('deal7d')
                print(item)
                data.append(item)
f=open('data_new.txt','w',encoding='utf8')
f.write(str(data))

# f=open('data_count.txt','r',encoding='utf8')
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




# headers={
#         'X-Requested-With':'XMLHttpRequest',
#         'Referer':'https://xueqiu.com/u/4008570681',
#         'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
#         'Cookie':'device_id=1d997a818b7d1bd58eb4992f799a760a; xq_a_token=dd443faf4b7df7a4ed1e29049e2840e2133449fd;',
#         }
# url=' https://xueqiu.com/v4/statuses/user_timeline.json?page=7&user_id=4008570681'
# response=requests.get(url,headers=headers)
# print(response.text)
# result = json.loads(response.text)
# statuses = result.get('statuses')
# maxpage = result.get('maxPage')
# if statuses:
#     status_item={}
#     for status in statuses:
#         status_item['user']=status.get('user').get('screen_name')
#         status_item['created_time']=status.get('created_at')
#         status_item['article_id']=status.get('id')
#         status_item['article']=status.get('text')
#         status_item['retweet_count']=status.get('retweet_count')
#         status_item['reply_count']=status.get('reply_count')
#         status_item['fav_count']=status.get('like_count')
#         print(status_item)