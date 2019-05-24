# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from copy import deepcopy
from urllib.parse import urljoin
import json
from lxml import etree

class DdSpider(scrapy.Spider):
    name = 'dd'
    allowed_domains = ['dangdang.com']
    start_urls = ['http://book.dangdang.com/']
    redis_key = 'dd' #lpush dd 'http://book.dangdang.com/'

    def parse(self, response):
        div_list = response.xpath('//*[@id="bd_auto"]//div[@class="con flq_body"]/div')
        for div in div_list:
            item = {}
            item['b_cate'] = div.xpath('./dl/dt//text()').extract()
            item['b_cate'] = [i.strip() for i in item['b_cate'] if len(i.strip()) > 0]
            dl_list = div.xpath('./div//dl[@class="inner_dl"]')
            for dl in dl_list:
                item['m_cate'] = dl.xpath('./dt//text()').extract()
                item['m_cate'] = [i.strip() for i in item['m_cate'] if len(i.strip()) > 0][0]
                a_list = dl.xpath('./dd/a')
                for a in a_list:
                    item['s_href'] = a.xpath('./@href').extract_first()
                    item['s_cate'] = a.xpath('.//text').extract_first()
                    if item['s_href'] is not None:
                        yield scrapy.Request(
                            item['s_href'],
                            callback=self.parse_book_list,
                            meta={'item': deepcopy(item)}
                        )

    def parse_book_list(self, response):
        item = response.meta['item']
        li_list = response.xpath('//ul[@class="bigimg"]/li')
        for li in li_list:
            item['img'] = li.xpath('./a[@class="pic"]/img/@src').extract_first()
            if item['img'] == 'images/model/guan/url_none.png':
                item['img'] = li.xpath('./a[@class="pic"]/img/@data-original').extract_first()
            item['name'] = li.xpath('./p[@class="name"]/a/@title').extract_first()
            item['desc'] = li.xpath('./p[@class="detail"]/text()').extract_first()
            item['price'] = li.xpath('.//span[@class="search_now_price"]/text()').extract_first()
            item['author'] = li.xpath('./p[@class="search_book_author"]/span[1]/a/text()').extract()
            item['publish_date'] = li.xpath('./p[@class="search_book_author"]/span[2]/text()').extract_first()
            item['press'] = li.xpath('./p[@class="search_book_author"]/span[3]/a/text()').extract_first()
            item['sku_id'] = li.xpath('./@sku').extract_first()
            print(item)

            yield scrapy.Request(
                'http://product.dangdang.com/index.php?r=comment%2Flist&productId={}&mainProductId={}&pageIndex=1'.format(item['sku_id'], item['sku_id']),
                callback=self.parse_comment_summary,
                meta={'item': deepcopy(item)}
            )

            yield scrapy.Request(
                'http://product.dangdang.com/index.php?r=comment%2Flist&productId={}&mainProductId={}&pageIndex=1'.format(item['sku_id'],item['sku_id']),
                callback=self.parse_comment,
                meta={'sku_id': item['sku_id'], 'page': 1}
            )

        next_url = response.xpath('//li[@class="next"]/a/@href').extract_first()
        if next_url is not None:
            yield scrapy.Request(
                urljoin(response.url, next_url),
                callback=self.parse_book_list,
                meta={'item': item}
            )

    def parse_comment_summary(self, response):
        item = response.meta['item']
        res = json.loads(response.text)['data']['list']['summary']
        item['rate'] = res['goodRate']
        item['all_comment_count'] = res['total_all_comment_num']
        item['good_comment_count'] = res['total_crazy_count']
        item['poor_comment_count'] = res['total_detest_count']
        item['image_comment_count'] = res['total_image_count']
        yield item

    def parse_comment(self, response):
        sku_id = response.meta['sku_id']
        page = response.meta['page']
        res = json.loads(response.text)
        html = res['data']['list']['html']
        comments = etree.HTML(html).xpath('//div[@class="comment_items clearfix"]')
        maxPage = res['data']['list']['summary']['pageCount']
        for comment in comments:
            item = {}
            item['sku_id'] = sku_id
            item['score'] = comment.xpath('./div/div[@class="pinglun"]/em/text()')[0]
            item['desc'] = ''.join(comment.xpath('./div/div[@class="describe_detail"]//text()')).strip()
            item['create_time'] = comment.xpath('./div/div[@class="starline clearfix"]/span/text()')[0]
            item['support'] = comment.xpath('./div/div[@class="support"]/a[1]/text()')[0]
            yield item

        if page < maxPage:
            page += 1
            yield scrapy.Request(
                'http://product.dangdang.com/index.php?r=comment%2Flist&productId={}&mainProductId={}&pageIndex={}'.format(sku_id, sku_id, page),
                callback=self.parse_comment,
                meta={'sku_id': sku_id, 'page': page}
            )







