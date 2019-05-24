
import re
import requests
import json
import time
from random import choice
import pymongo



cookies=['c906a480552717666c3e3ec4bc0d0fc57309e471','37fc1735d21daea9d4e775b190bda674b8af74ac','5303d95c3b4ffef888401849ee15f382667e8f6e',
         'e41ec0d9001db0743e4770e112a39c92652b4cd4','71c5cbb7171116b22c6f91b404d2cfa61d656a6d','0c090c0bc6311907a205b3aad0084e4df078a4d8',
         ]
url='https://xueqiu.com/statuses/search.json?count=10&comment=0&symbol={}&hl=0&source=user&sort=time&page={}&q='
pattern1=re.compile('(我刚刚关注了)*.*?\$.*?\$.*?当前价.*',re.S)
pattern2=re.compile('(在￥.*?)*关注((股票)|(基金)|(<a)).*?\$.*?\$.*',re.S)
pattern3=re.compile('我刚刚在.*?委托((买入)|(卖出)).*?\$.*?\$.*',re.S)
pattern4=re.compile('.*?以((￥)|(undefined)).*?((买入)|(卖出)).*?\$.*?\$.*',re.S)
pattern5=re.compile('将.*?\$.*?\$.*?目标价调整.*',re.S)
pattern6=re.compile('.*?使用模拟盈亏以.*?\$.*?\$.*',re.S)
pattern7=re.compile('.*?组合.*?\$.*?ZH.*?\$.*',re.S)

MONGO_URL='192.168.1.161'
MONGO_DB='test'
MONGO_PORT=27017

class XueqiuAdd():
    def __init__(self,mongo_url=MONGO_URL,mongo_db=MONGO_DB,mongo_port=MONGO_PORT):
        self.client = pymongo.MongoClient(host=mongo_url, port=mongo_port)
        self.auth = self.client.admin
        self.auth.authenticate('spyder', 'knquant123')
        self.db = self.client[mongo_db]

    def __del__(self):
        self.client.close()

    def process_item(self,item):
        cntime = time.strftime('%Y-%m-%d %H:%M', time.localtime(int(str(item.get('created_time'))[:10])))
        item['created_time']=cntime
        symbol=item['collection'][0]
        article=item['article']
        pattern = re.compile('([630]0\d{4})')
        #pattern = re.compile('([08]\d{4})\D')
        codes = re.findall(pattern, item['article'])
        collection=[]
        for code in codes:
            if re.match('^6', code):
                temp = 'SH' + code
                if temp not in collection:
                    collection.append(temp)
            else:
                temp = 'SZ' + code
                if temp not in collection:
                    collection.append(temp)
        # for code in codes:
        #    if code not in collection:
        #        collection.append(code)
        item['collection']=collection
        if re.match(pattern1, article) or re.match(pattern2, article):
            item['article_type']='follow'
        elif re.match(pattern3, article) or re.match(pattern4, article) or re.match(pattern5, article) or re.match(
                pattern6, article):
            item['article_type'] = 'trans'
        elif re.match(pattern7, article):
            item['article_type'] = 'combine'
        else:
            item['article_type'] = 'discuss'

        self.db[symbol].update({'article_id': dict(item).get('article_id')}, {'$set': item}, True)

    def get_item(self,url,cookie):
        headers = {
            'Host': 'xueqiu.com',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
        }
        headers.update({'Cookie': 'xq_a_token={}'.format(cookie)})
        res = requests.get(url, headers=headers)
        #print(res.text)
        result = json.loads(res.text)
        statuses = result.get('list')
        symbol = result.get('symbol')
        if statuses:
            status_item = {}
            for status in statuses:
                status_item['collection'] = [symbol]
                status_item['user'] = status.get('user').get('screen_name')
                status_item['created_time'] = status.get('created_at')
                status_item['title']=status.get('title')
                status_item['article_id'] = status.get('id')
                status_item['article'] = status.get('text')
                status_item['retweet_count'] = status.get('retweet_count')
                status_item['reply_count'] = status.get('reply_count')
                status_item['fav_count'] = status.get('like_count')
                status_item['article_type']=''
                yield status_item
                #print(status_item)
        else:
            yield None
            print(res.text)
            print(url,cookie)
            #f=open('add_pages.txt','a',encoding='utf8')
            #f.write(url+'\n')
            #time.sleep(5)

    def main(self):
        headers={
            'Host': 'xueqiu.com',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
            'Cookie':'xq_a_token=c906a480552717666c3e3ec4bc0d0fc57309e471'
        }
        rank_url='https://xueqiu.com/stock/screener/screen.json?category=SH&orderby=tweet7d&order=desc&page={}&tweet7d=ALL'
        for i in range(1,121):
            response=requests.get(rank_url.format(i),headers=headers)
            results=json.loads(response.text)['list']
            for result in results:
                code=result['symbol']
        # with open('stockname.txt','r',encoding='utf8') as f:
        #     for temp in eval(f.read()):
        #         code=temp[-5:]
                res = requests.get(url.format(code,1), headers=headers)
                maxpage=json.loads(res.text)['maxPage']
                for page in range(1,int(maxpage)+1):
                    items=self.get_item(url.format(code,page),choice(cookies))
                    last_item={}
                    for item in items:
                        if item:
                            self.process_item(item)
                            last_item=item
                        else:
                            print('failed')
                            time.sleep(10)
                            items = self.get_item(url.format(code, page), choice(cookies))
                            for item in items:
                                if item:
                                    self.process_item(item)
                                    last_item=item

                    if last_item:
                        last_time = int(time.mktime(time.strptime(last_item.get('created_time'),'%Y-%m-%d %H:%M')))
                        end_time = int(time.time()) - 1 * 24 * 60 * 60
                        if last_time < end_time:
                            break
                    #time.sleep(0.5)
                print(code)
            print(i)

if __name__=='__main__':
    add=XueqiuAdd()
    add.main()