# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


import pymongo
from zhilian.items import JobItem
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
        with open('/home/jbliu/projects/zhilian/stockname.txt','r',encoding='utf-8') as f:
            colls=eval(f.read())
        return colls

    def open_spider(self,spider):
        self.client = pymongo.MongoClient(host=self.mongo_url, port=self.mongo_port)
        self.auth = self.client.admin
        self.auth.authenticate('spyder', 'knquant123')
        self.db = self.client[self.mongo_db]
        for coll in self.get_colls():
            code=coll[-8:]
            self.db[code].create_index([('jobId',pymongo.DESCENDING)])



    def close_spider(self,spider):
        self.client.close()


    def process_item(self, item, spider):
        self.db[item['collection']].update({'jobId': dict(item).get('jobId')}, {'$set': item}, True)
        return item
