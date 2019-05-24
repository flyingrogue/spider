# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class UserItem(scrapy.Item):
    collection='Userinfo'
    uid = scrapy.Field()
    name = scrapy.Field()
    stocks = scrapy.Field()
    status = scrapy.Field()
    fans = scrapy.Field()

class StatusItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    collection=scrapy.Field()
    user=scrapy.Field()
    created_time=scrapy.Field()
    article_id=scrapy.Field()
    article_type=scrapy.Field()
    article=scrapy.Field()
    retweet_count=scrapy.Field()
    reply_count=scrapy.Field()
    fav_count=scrapy.Field()
