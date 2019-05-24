# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


import pymongo
from xueqiu.items import UserItem,StatusItem
import time
import re
from scrapy.exceptions import DropItem

class MongoPipeline(object):
    def __init__(self,mongo_url,mongo_db,mongo_port):
        self.mongo_url = mongo_url
        self.mongo_db = mongo_db
        self.mongo_port = mongo_port

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_url=crawler.settings.get('MONGO_URL'), mongo_db=crawler.settings.get('MONGO_DB'),
            mongo_port=crawler.settings.get('MONGO_PORT')
        )

    def get_colls(self):
        with open('stockcode.txt','r',encoding='utf-8') as f:
            stocks=f.read()
            colls=eval(stocks)
        return colls

    def open_spider(self,spider):
        self.client = pymongo.MongoClient(host=self.mongo_url, port=self.mongo_port)
        self.auth = self.client.admin
        self.auth.authenticate('spyder', 'knquant123')
        self.db = self.client[self.mongo_db]
        self.db[UserItem.collection].create_index([('uid', pymongo.ASCENDING)])
        for coll in self.get_colls():
            code=re.findall('.*?(S[ZH]\d+)',coll)[0]
            self.db[code].create_index([('article_id',pymongo.DESCENDING)])



    def close_spider(self,spider):
        self.client.close()

    # def parse_item(self,text):
    #     pattern = re.compile('\$.*?\((S[HZ].*?)\)\$')
    #     symbols = re.findall(pattern, text)
    #     return symbols

    def process_item(self, item, spider):
        if isinstance(item,UserItem):
            self.db[item.collection].update({'uid':dict(item).get('uid')},{'$set':item},True)
            #return item
        if isinstance(item,StatusItem):
            #symbols=self.parse_item(dict(item)['article'])
            #if symbols:
                #for symbol in symbols:
                    #self.db[symbol].update({'article_id':dict(item).get('article_id')},{'$set':item},True)
            #else:
                #raise DropItem('废物数据')

            for coll in item['collection']:
                self.db[coll].update({'article_id': dict(item).get('article_id')}, {'$set': item}, True)
        return item

#将时间戳改为正常时间
class TimePipeline():
    def parse_time(self,date):
        cntime=time.strftime('%Y-%m-%d %H:%M',time.localtime(int(str(date)[:10])))
        return cntime

    def process_item(self,item,spider):
        if isinstance(item,StatusItem):
            item['created_time']=self.parse_time(item.get('created_time'))
        return item

#清除废物数据
class DuplicatePipeline():
    def parse_item(self, text):
        pattern = re.compile('\$.*?\((S[HZ][630]\d+)\)\$')
        symbols = re.findall(pattern, text)
        return symbols

    def process_item(self,item,spider):
        if isinstance(item,StatusItem):
            text=dict(item)['article']
            symbols=self.parse_item(text)
            if symbols:
                item['collection']=symbols
                return item
            else:
                raise DropItem('废物数据')
        return item

#对数据进行分类
class TypePipeline():
    def __init__(self):
        self.pattern1=re.compile('(我刚刚关注了)*.*?\$.*?\$.*?当前价.*', re.S)
        self.pattern2 = re.compile('(在￥.*?)*关注((股票)|(基金)|(<a)).*?\$.*?\$.*', re.S)
        self.pattern3 = re.compile('我刚刚在.*?委托((买入)|(卖出)).*?\$.*?\$.*', re.S)
        self.pattern4 = re.compile('.*?以((￥)|(undefined)).*?((买入)|(卖出)).*?\$.*?\$.*', re.S)
        self.pattern5 = re.compile('将.*?\$.*?\$.*?目标价调整.*', re.S)
        self.pattern6 = re.compile('.*?使用模拟盈亏以.*?\$.*?\$.*', re.S)
        self.pattern7 = re.compile('.*?组合.*?\$.*?ZH.*?\$.*', re.S)

    def process_item(self,item,spider):
        if isinstance(item, StatusItem):
            if re.match(self.pattern1, item['article']) or re.match(self.pattern2, item['article']):
                item['article_type']='follow'
                return item
            elif re.match(self.pattern3, item['article']) or re.match(self.pattern4, item['article']) or re.match(self.pattern5,
                item['article'])or re.match(self.pattern6,item['article']):
                item['article_type']='trans'
                return item
            elif re.match(self.pattern7, item['article']):
                item['article_type'] = 'combine'
                return item
            else:
                item['article_type']='discuss'
                return item