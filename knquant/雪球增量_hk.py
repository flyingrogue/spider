# -*- coding: utf-8 -*-

import re
import requests
from requests.exceptions import ProxyError
from urllib3.exceptions import MaxRetryError
import json
import time
from random import choice
import pymongo

proxyHost = "http-dyn.abuyun.com"
proxyPort = "9020"
proxyUser = "HP7Y01400L962MUD"
proxyPass = "ED8926D78920DD44"

MONGO_URL = '192.168.1.161'
MONGO_DB = 'XueQiuStock'
MONGO_PORT = 27017

pattern1 = re.compile('(我刚刚关注了)*.*?\$.*?\$.*?当前价.*', re.S)
pattern2 = re.compile('(在￥.*?)*关注((股票)|(基金)|(<a)).*?\$.*?\$.*', re.S)
pattern3 = re.compile('我刚刚在.*?委托((买入)|(卖出)).*?\$.*?\$.*', re.S)
pattern4 = re.compile('.*?以((￥)|(undefined)).*?((买入)|(卖出)).*?\$.*?\$.*', re.S)
pattern5 = re.compile('将.*?\$.*?\$.*?目标价调整.*', re.S)
pattern6 = re.compile('.*?使用模拟盈亏以.*?\$.*?\$.*', re.S)
pattern7 = re.compile('.*?组合.*?\$.*?ZH.*?\$.*', re.S)


class XueqiuAdd():
    def __init__(self, mongo_url=MONGO_URL, mongo_db=MONGO_DB, mongo_port=MONGO_PORT):
        self.client = pymongo.MongoClient(host=mongo_url, port=mongo_port)
        self.auth = self.client.admin
        self.auth.authenticate('spyder', 'knquant123')
        self.db = self.client[mongo_db]

    def __del__(self):
        self.client.close()

    # 数据处理
    def process_item(self, item):
        cntime = time.strftime('%Y-%m-%d %H:%M', time.localtime(int(str(item.get('created_time'))[:10])))
        item['created_time'] = cntime
        symbol = item['collection'][0]
        article = item['article']
        pattern = re.compile('([08]\d{4})\D')
        codes = re.findall(pattern, item['article'])
        collection = []
        for code in codes:
           if code not in collection:
               collection.append(code)
        item['collection'] = collection
        if re.match(pattern1, article) or re.match(pattern2, article):
            item['article_type'] = 'follow'
        elif re.match(pattern3, article) or re.match(pattern4, article) or re.match(pattern5, article) or re.match(
                pattern6, article):
            item['article_type'] = 'trans'
        elif re.match(pattern7, article):
            item['article_type'] = 'combine'
        else:
            item['article_type'] = 'discuss'

        self.db[symbol].update({'article_id': dict(item).get('article_id')}, {'$set': item}, True)

    # 解析json
    def get_item(self, url):
        res = self.get_res(url)
        # print(res.text)
        result = json.loads(res.text)
        statuses = result.get('list')
        symbol = result.get('symbol')
        if statuses:
            status_item = {}
            for status in statuses:
                status_item['collection'] = [symbol]
                status_item['user'] = status.get('user').get('screen_name')
                status_item['created_time'] = status.get('created_at')
                status_item['title'] = status.get('title')
                status_item['article_id'] = status.get('id')
                status_item['article'] = status.get('text')
                status_item['retweet_count'] = status.get('retweet_count')
                status_item['reply_count'] = status.get('reply_count')
                status_item['fav_count'] = status.get('like_count')
                status_item['article_type'] = ''
                yield status_item
                # print(status_item)
        else:
            yield None
            print(res.text)

    # 访问首页取得cookie，再请求所需页面
    def get_res(self, url):
        headers = {
            'Host': 'xueqiu.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
            #'Cookie': 'xq_a_token=243bb1cce89c8d4d365a26452e50d6e62b83db37;'
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
        res = None
        while True:
            try:
                sess = requests.session()
                sess.get('https://xueqiu.com/', headers=headers, proxies=proxies, timeout=5)
                res = sess.get(url, headers=headers, proxies=proxies, timeout=5)
            except (OSError, TimeoutError, MaxRetryError, ProxyError) as e:
                pass
            if res and re.match('{.*}', res.text, re.S):
                break
        return res

    def main(self):
        url = 'https://xueqiu.com/statuses/search.json?count=10&comment=0&symbol={}&hl=0&source=user&sort=time&page={}&q='
        with open('/home/jbliu/projects/stockcode_hk.txt','r',encoding='utf8') as f:
            for temp in eval(f.read()):
                code=temp[-5:]
                res = self.get_res(url.format(code, 1))
                maxpage = json.loads(res.text)['maxPage']
                for page in range(1, int(maxpage) + 1):
                    items = self.get_item(url.format(code, page))
                    last_item = {}
                    for item in items:
                        if item:
                            self.process_item(item)
                            last_item = item
                        else:
                            print('failed')
                            #time.sleep(2)
                            items = self.get_item(url.format(code, page))
                            for item in items:
                                if item:
                                    self.process_item(item)
                                    last_item = item
                                    
                    # 判断爬取到哪一天，若到了截止时间则终止此只股票的遍历
                    if last_item:
                        last_time = int(time.mktime(time.strptime(last_item.get('created_time'), '%Y-%m-%d %H:%M')))
                        end_time = int(time.time()) - 3 * 24 * 60 * 60
                        if last_time < end_time:
                            break
                    # time.sleep(0.5)
                print(code)



if __name__ == '__main__':
    add = XueqiuAdd()
    add.main()