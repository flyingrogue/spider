# -*- coding: utf-8 -*-
import scrapy
from urllib.parse import urljoin
from copy import deepcopy
import json

class JdSpider(scrapy.Spider):
    name = 'jd'
    allowed_domains = ['jd.com','p.3.cn']
    start_urls = ['https://book.jd.com/booksort.html']

    def parse(self, response):
        dt_list = response.xpath('//*[@id="booksort"]/div[@class="mc"]/dl/dt')
        for dt in dt_list:
            item = {}
            item['b_cate'] = dt.xpath('./a/text()').extract_first()
            em_list = dt.xpath('./following-sibling::dd[1]/em')
            for em in em_list:
                item['s_href'] = em.xpath('./a/@href').extract_first()
                item['s_cate'] = em.xpath('/a/text()').extract_first()
                if item['s_href'] is not None:
                    item['s_href'] = urljoin(response.url,item['s_href'])
                    yield scrapy.Request(
                        item['s_href'],
                        callback=self.parse_book_list,
                        meta={'item': deepcopy(item)}
                    )


    def parse_book_list(self, response):
        item = response.meta['item']
        li_list = response.xpath('//*[@id="plist"]/ul/li[@class="gl-item"]')
        for li in li_list:
            item['img'] = li.xpath('.//div[@class="p-img"]//img/@src').extract_first()
            if item['img'] is None:
                item['img'] = li.xpath('.//div[@class="p-img"]//img/@data-lazy-img').extract_first()
            item['img'] = 'https:' + item['img'] if item['img'] is not None else None
            item['name'] = li.xpath('.//div[@class="p-name"]/a/em/text()').extract_first().strip()
            item['author'] = li.xpath('.//span[@class="author_type_1"]/a/text()').extract()
            item['press'] = li.xpath('.//span[@class="p-bi-store"]/a/text()').extract_first()
            item['publish_date'] = li.xpath('.//span[@class="p-bi-date"]/text()').extract_first().strip()
            item['sku_id'] = li.xpath('./div/@data-sku').extract_first()
            yield scrapy.Request(
                'https://p.3.cn/prices/mgets?skuIds=J_{}'.format(item['sku_id']),
                callback=self.parse_book_price,
                meta={'item': deepcopy(item)}
            )

            yield scrapy.Request(
                'https://club.jd.com/comment/skuProductPageComments.action?productId={}&score=0&sortType=6&page=0&pageSize=10'.format(item['sku_id']),
                callback=self.parse_comment,
                meta={'sku_id': item['sku_id'], 'page': 0}
            )

        next_url = response.xpath('//a[@class="pn-next"]/@href').extract_first()
        if next_url is not None:
            next_url = urljoin(response.url,next_url)
            yield scrapy.Request(
                next_url,
                callback=self.parse_book_list,
                meta={'item': item}
            )

    def parse_book_price(self,response):
        item = response.meta['item']
        item['book_price'] = json.loads(response.text)[0]['op']
        yield scrapy.Request(
            'https://club.jd.com/comment/skuProductPageComments.action?productId={}&score=0&sortType=6&page=0&pageSize=10'.format(item['sku_id']),
            callback=self.parse_comment_summary,
            meta={'item': item}
        )

    def parse_comment_summary(self,response):
        item = response.meta['item']
        res = json.loads(response.text)['productCommentSummary']
        item['rate'] = res['goodRateShow']
        item['sum_comment'] = res['commentCount']
        item['default_comment'] = res['defaultGoodCount']
        item['good_comment'] = res['goodCount']
        item['poor_comment'] = res['poorCount']
        item['show_comment'] = res['showCount']
        yield item

    def parse_comment(self,response):
        sku_id = response.meta['sku_id']
        page = response.meta['page']
        res = json.loads(response.text)
        comments = res['comments']
        maxPage = res['maxPage']
        for comment in comments:
            item = {}
            item['comment_id'] = comment['id']
            item['create_time'] = comment['creationTime']
            item['score'] = comment['score']
            item['sku_id'] = sku_id
            item['book_name'] = comment['productColor']
            item['content'] = comment['content']
            yield item

        if page < int(maxPage)-1:
            page += 1
            yield scrapy.Request(
                'https://club.jd.com/comment/skuProductPageComments.action?productId={}&score=0&sortType=6&page={}&pageSize=10'.format(sku_id, page),
                callback=self.parse_comment,
                meta={'sku_id': sku_id, 'page': page}
            )







