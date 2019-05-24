# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy_redis.spiders import RedisCrawlSpider
import re
from lxml import etree


class AmazonSpider(RedisCrawlSpider):
    name = 'amazon'
    allowed_domains = ['amazon.cn']
    start_urls = ['http://amazon.cn/']
    redis_key = 'amazon'

    rules = (
        Rule(LinkExtractor(restrict_xpaths=('//h3[text()="筛选："]/preceding-sibling::ul[1]/ul//li',)), follow=True),
        Rule(LinkExtractor(restrict_xpaths=('//div[@id="mainResults"]/ul/li//h2/..',)), callback='parse_book_detail'),
        Rule(LinkExtractor(restrict_xpaths=('//a[@id="pagnNextLink"]',)), follow=True)
    )

    def parse_book_detail(self, response):
        item = {}
        item['sku_id']=response.url.split('/')[4]
        item['title'] = response.xpath('//[@id="productTitle"]/text()').extract_first()
        item['publish_date'] = response.xpath('//h1[@id="title"]/span[last()]/text()').extract_first()
        item['author'] = response.xpath('//div[@id="byline"]/span[@class="author notFaded"]/a/text()').extract()
        item['img'] = response.xpath('//div[@id="img-canvas"]/img/@src').extract_first()
        item['price'] = response.xpath('//div[@id="soldByThirdParty"]/span[2]/text()').extract_first()
        item['cate'] = response.xpath('//div[@id="wayfinding-breadcrumbs_feature_div"]//a/text()').extract()
        item['cate'] = [i.strip() for i in item["cate"]]
        item['press'] = response.xpath('//b[text()="出版社:"]/../text()').extract_first()
        item['desc'] = re.findall(r'<noscript>.*?<div>(.*?)</div>.*?</noscript>', response.text, re.S)
        item['desc'] = item["desc"][0].split("<br>", 1)[0] if len(item["desc"]) > 0 else None
        #item['desc'] = response.xpath('//noscript/div/text()').extract()
        #item['desc'] = [i.strip() for i in item["desc"] if len(i.strip()) > 0 and i != "海报: "]
        yield item

        yield scrapy.FormRequest(
            'https://www.amazon.cn/hz/reviews-render/ajax/reviews/get/',
            formdata={
                'reviewerType': 'all_reviews',
                'pageNumber': 1,
                'pageSize': 10, #可调整为20
                'asin': item['sku_id'],
            },
            callback=self.parse_book_comment,
            meta={'sku_id': item['sku_id'], 'page': 1}
        )

    def parse_book_comment(self, response):
        sku_id = response.meta['sku_id']
        page = response.meta['page']
        lis = response.text.split('&&&')
        for li in lis[5:-5]:
            item = {}
            html = eval(li.strip())[2]
            html = etree.HTML(html)
            item['sku_id'] = sku_id
            item['comment_id'] = html.xpath('//div[@data-hook="review"]/@id')[0]
            item['star'] = html.xpath('//i[@data-hook="review-star-rating"]/span/text()')[0]
            item['title'] = html.xpath('//a[@data-hook="review-title"]/span/text()')[0]
            item['date'] = html.xpath('//span[@data-hook="review-date"]/text()')[0]
            item['content'] = html.xpath('//span[@data-hook="review-body"]/span/text()')[0]
            yield item
            print(item)

        if not re.match(r'.*?a-last\\">下一页<.*',lis[-3],re.S):
            page += 1
            yield scrapy.FormRequest(
                'https://www.amazon.cn/hz/reviews-render/ajax/reviews/get/',
                formdata={
                    'reviewerType': 'all_reviews',
                    'pageNumber': page,
                    'pageSize': 10,  # 可调整为20
                    'asin': sku_id,
                },
                callback=self.parse_book_comment,
                meta={'sku_id': sku_id, 'page': page}
            )

