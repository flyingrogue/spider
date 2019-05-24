# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
import re
import json
from xueqiu.items import UserItem,StatusItem



class SnowballSpider(scrapy.Spider):
    name = 'snowball'
    allowed_domains = ['xueqiu.com']

    stock_url='https://xueqiu.com/S/{code}'
    fan_url='https://xueqiu.com/S/{code}/follows?page={page}'
    user_url='https://xueqiu.com/v4/statuses/user_timeline.json?page={page}&user_id={uid}'


    # def start_requests(self):
    #     with open('/home/jbliu/projects/xueqiu/stockcode.txt','r',encoding='utf-8') as f:
    #         stocks=f.read()
    #         # for num in eval(stocks):
    #         #     if re.match('^6', num):
    #         #         code = 'SH' + num
    #         #     else:
    #         #         code = 'SZ' + num
    #         for stock in eval(stocks):
    #             code=re.findall('.*?(S[ZH]\d+)',stock)[0]
    #             yield Request(self.fan_url.format(code=code,page=1),callback=self.parse_fans,meta={'page':1,'code':code},
    #                           headers={
    #                               'Referer': 'https://xueqiu.com/S/{code}'.format(code=code),
    #                               'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
    #                               'Cookie': 'xq_a_token=7b6f00303fcba4299fda41c6ab43557664c19906; xq_r_token=c73ecdd81e92fbf1389a1413d51519fe56044ed3',
    #                           },dont_filter=True)
    #             print('@'*100)

    # def start_requests(self):
    #     with open('/home/jbliu/projects/xueqiu/urls.txt','r',encoding='utf-8') as f:
    #         urls=f.readlines()
    #         pattern=re.compile('.*/(S[HZ]\d+).*=(\d+)')
    #         for url in urls:
    #             temp=re.findall(pattern,url)[0]
    #             code=temp[0]
    #             page=int(temp[1])
    #             yield Request(self.fan_url.format(code=code, page=page), callback=self.parse_fans,
    #                           meta={'page': page, 'code': code},
    #                           headers={
    #                               'Referer': 'https://xueqiu.com/S/{code}'.format(code=code),
    #                               'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
    #                               'Cookie': 'xq_a_token=7b6f00303fcba4299fda41c6ab43557664c19906; xq_r_token=c73ecdd81e92fbf1389a1413d51519fe56044ed3',
    #                           }, dont_filter=True)
    #             print('@'*100)

    def start_requests(self):
        with open('/home/jbliu/projects/xueqiu/user_url.txt','r',encoding='utf-8') as f:
            urls=f.readlines()
            pattern=re.compile('.*page=(\d+).*=(.*)')
            for url in urls:
                temp=re.findall(pattern,url)[0]
                uid=temp[1]
                page=int(temp[0])
                yield Request(self.user_url.format(uid=uid,page=page),callback=self.parse_user,meta={'uid':uid,'page':page},
                              dont_filter=True)
                print('@'*100)

    # #解析粉丝列表
    # def parse_fans(self, response):
    #     globals = {
    #         'true': 0,
    #         'false': 1,
    #         'null': 0
    #     }
    #     code = response.meta.get('code')
    #     page = response.meta.get('page')
    #     pattern = re.compile('followers":(.*),"an.*?"maxPage":(\d+)};', re.S)
    #     result = re.findall(pattern, response.text)
    #     if result:
    #         #用户个人信息
    #         lis = eval(result[0][0], globals)
    #         user_item=UserItem()
    #         for li in lis:
    #             user_item['uid'] = li['id']
    #             user_item['name'] = li['screen_name']
    #             user_item['stocks'] = li['stocks_count']
    #             user_item['status'] = li['status_count']
    #             user_item['fans'] = li['followers_count']
    #             yield user_item

                # #用户第一页帖子
                # uid=li['id']
                # yield Request(self.user_url.format(uid=uid,page=1), callback=self.parse_user,meta={'page':1,'uid':uid},
                #               headers={
                #                   'X-Requested-With':'XMLHttpRequest',
                #                   'Referer':'https://xueqiu.com/u/{uid}'.format(uid=uid),
                #                   'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
                #                   'Cookie':'xq_a_token=7b6f00303fcba4299fda41c6ab43557664c19906; xq_r_token=c73ecdd81e92fbf1389a1413d51519fe56044ed3',
                #               },dont_filter=True)

        #     #下一页粉丝
        #     maxpage=int(result[0][1])
        #     if int(page) < maxpage:
        #         page = int(page) + 1
        #         yield Request(self.fan_url.format(code=code,page=page),callback=self.parse_fans,meta={'page':page,'code':code},
        #                         headers={
        #                               'Referer': 'https://xueqiu.com/S/{code}/follows?page={page}'.format(code=code, page=page - 1),
        #                               'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
        #                               'Cookie':'xq_a_token=7b6f00303fcba4299fda41c6ab43557664c19906; xq_r_token=c73ecdd81e92fbf1389a1413d51519fe56044ed3',
        #                           },dont_filter=True)
        #         with open('/home/jbliu/projects/xueqiu/pages.txt','r',encoding='utf-8') as f:
        #             x=f.read()
        #         y=eval(x)
        #         y[code]=page
        #         with open('/home/jbliu/projects/xueqiu/pages.txt', 'w', encoding='utf-8') as f:
        #             f.write(str(y))
        # else:
        #     with open('/home/jbliu/projects/xueqiu/fans_url.txt','a',encoding='utf-8') as f:
        #         f.write('https://xueqiu.com/S/{code}/follows?page={page}'.format(code=code,page=page)+'\n')


    #解析用户帖子列表
    def parse_user(self,response):
        uid = response.meta.get('uid')
        page = response.meta.get('page')
        if re.match('^{"count".*}$', response.text, re.S):
            result = json.loads(response.text)
            statuses = result.get('statuses')
            maxpage = result.get('maxPage')
            if statuses:
                status_item=StatusItem()
                for status in statuses:
                    status_item['user']=status.get('user').get('screen_name')
                    status_item['created_time']=status.get('created_at')
                    status_item['article_id']=status.get('id')
                    status_item['article']=status.get('text')
                    status_item['retweet_count']=status.get('retweet_count')
                    status_item['reply_count']=status.get('reply_count')
                    status_item['fav_count']=status.get('like_count')
                    yield status_item

            #下一页帖子
            if int(page) < int(maxpage):
                page = int(page) + 1
                yield Request(self.user_url.format(uid=uid, page=page), callback=self.parse_user,meta={'uid': uid, 'page': page},
                              dont_filter=True)
        else:
            with open('/home/jbliu/projects/xueqiu/urls.txt', 'a', encoding='utf-8') as f:
                f.write('https://xueqiu.com/v4/statuses/user_timeline.json?page={page}&user_id={uid}'.format(uid=uid,page=page) + '\n')

