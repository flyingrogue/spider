# -*- coding: utf-8 -*-

import re
import pymongo

MONGO_URL='192.168.1.161'
MONGO_DB='test'
MONGO_PORT=27017

class MongoAdd():
    def __init__(self,mongo_url=MONGO_URL,mongo_db=MONGO_DB,mongo_port=MONGO_PORT):
        self.client = pymongo.MongoClient(host=mongo_url, port=mongo_port)
        self.auth = self.client.admin
        self.auth.authenticate('spyder', 'knquant123')
        self.db1 = self.client[mongo_db]
        self.db2 = self.client[mongo_db]

    def __del__(self):
        self.client.close()


    def query(self):
        a=['关注股票<a href="http://xueqiu.com/S/SZ002007" target="_blank">$华兰生物(SZ002007)$</a>，买入目标价￥28.92。',
           '2017-08-05以￥32.67买入<a href="http://xueqiu.com/S/SZ002007" target="_blank">$华兰生物(SZ002007)$</a>。',
           '我刚刚在<a href="http://xueqiu.com/k?q=%23%E9%9B%AA%E7%90%83%E5%AE%9E%E7%9B%98%E4%BA%A4%E6%98%93%23" target="_blank">#雪球实盘交易#</a>委托买入<a href="http://xueqiu.com/S/SZ002007" target="_blank">$华兰生物(SZ002007)$</a>，委托买入价28.95。',
           '将<a href="http://xueqiu.com/S/SZ002007" target="_blank">$华兰生物(SZ002007)$</a>买入目标价调整为￥25。',
           '<a href="http://xueqiu.com/S/SZ000651" target="_blank">$格力电器(SZ000651)$</a>，当前价 ¥36.55。',
           '2018-12-06使用模拟盈亏以 36.47元买入 <a href="http://xueqiu.com/S/SZ000651" target="_blank">$格力电器(SZ000651)$</a>。',
           '我刚刚关注了股票<a href="http://xueqiu.com/S/SZ000895" target="_blank">$双汇发展(SZ000895)$</a>，当前价 ¥21.70。',
           '2018-06-20以undefined47.952买入<a href="http://xueqiu.com/S/SZ000651" target="_blank">$格力电器(SZ000651)$</a>。',
           '在￥47.88时关注股票<a href="http://xueqiu.com/S/SZ000651" target="_blank">$格力电器(SZ000651)$</a>。',
           '<a href="http://xueqiu.com/S/SZ000799" target="_blank">$酒鬼酒(SZ000799)$</a> 吃吃吃上车',
           '我刚刚在<a href="http://xueqiu.com/k?q=%23%E9%9B%AA%E7%90%83%E5%AE%9E%E7%9B%98%E4%BA%A4%E6%98%93%23" targe="_blank">#雪球实盘交易#</a>委托卖出<a href="http://xueqiu.com/S/SZ000651" target="_blank">$格力电器(SZ000651)$</a>，委托卖出价40.5。']
        pattern1=re.compile('(我刚刚关注了)*.*?\$.*?\$.*?当前价.*',re.S)
        pattern2=re.compile('(在￥.*?)*关注((股票)|(基金)).*?\$.*?\$.*',re.S)
        pattern3=re.compile('我刚刚在.*?委托((买入)|(卖出)).*?\$.*?\$.*',re.S)
        pattern4=re.compile('.*?以((￥)|(undefined)).*?((买入)|(卖出)).*?\$.*?\$.*',re.S)
        pattern5=re.compile('将.*?\$.*?\$.*?目标价调整.*',re.S)
        pattern6=re.compile('.*?使用模拟盈亏以.*?\$.*?\$.*',re.S)
        pattern7=re.compile('我刚刚调整了.*?\$.*?\$.*',re.S)
        names=self.db2.list_collection_names()

        for i in a:
            if re.match(pattern1,i) or re.match(pattern2,i):

                print('关注类',i)
            elif re.match(pattern3,i) or re.match(pattern4,i) or re.match(pattern5,i) or re.match(pattern6,i) or re.match(pattern7,i):

                print('交易类',i)
            else:

                print('讨论类',i)
        print(re.match(pattern3,a[10]))





if __name__=='__main__':
    mongo=MongoAdd()
    mongo.query()