# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
import re
import json
from xueqiu.items import StatusItem
import time


class StockSpider(scrapy.Spider):
    name = 'snowball'
    allowed_domains = ['xueqiu.com']

    stock_url='https://xueqiu.com/S/{code}'
    fan_url='https://xueqiu.com/S/{code}/follows?page={page}'
    user_url='https://xueqiu.com/v4/statuses/user_timeline.json?page={page}&user_id={uid}'
    status_url='https://xueqiu.com/statuses/search.json?count=10&comment=0&symbol={code}&hl=0&source=user&sort=time&page={page}&q='

    def start_requests(self):
        with open('/home/jbliu/projects/xueqiu_add_hk/stockcode.txt','r',encoding='utf-8') as f:
            stocks=f.read()
            for stock in eval(stocks):
                code=stock[-5:]
                yield Request(self.status_url.format(code=code,page=1),callback=self.parse_status,meta={'page':1,'code':code},
                             dont_filter=True)
                print('@'*100)


    #解析股票帖子列表
    def parse_status(self,response):
        result = json.loads(response.text)
        statuses = result.get('list')
        symbol = result.get('symbol')
        maxpage=result.get('maxPage')
        code = response.meta.get('code')
        page = response.meta.get('page')
        last_time = int(time.time())
        if statuses:
            last_time = int(str(statuses[-1].get('created_at'))[:10])
            status_item=StatusItem()
            for status in statuses:
                status_item['collection']=[symbol]
                status_item['user']=status.get('user').get('screen_name')
                status_item['created_time']=status.get('created_at')
                status_item['title']=status.get('title')
                status_item['article_id']=status.get('id')
                status_item['article']=status.get('text')
                status_item['retweet_count']=status.get('retweet_count')
                status_item['reply_count']=status.get('reply_count')
                status_item['fav_count']=status.get('like_count')
                status_item['article_type']='discuss'
                yield status_item

            with open('/home/jbliu/projects/xueqiu_add_hk/pages.txt', 'r', encoding='utf-8') as f:
                x = f.read()
            y = eval(x)
            y[code] = page
            with open('/home/jbliu/projects/xueqiu_add_hk/pages.txt', 'w', encoding='utf-8') as f:
                f.write(str(y))
        # else:
        #     yield Request(self.status_url.format(code=code, page=page), callback=self.parse_status,meta={'code': code, 'page': page},
        #                   dont_filter=True)
        #     print('='*100)

        #下一页帖子
        end_time = int(time.time()) - 3 * 24 * 60 * 60
        if page < int(maxpage) and last_time > end_time:
            page = page + 1
            yield Request(self.status_url.format(code=code, page=page), callback=self.parse_status,meta={'code': code, 'page': page},
                          dont_filter=True)
