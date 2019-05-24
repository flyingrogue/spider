# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JobItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    collection=scrapy.Field()
    jobId=scrapy.Field()
    applyType=scrapy.Field()
    city=scrapy.Field()
    companyName=scrapy.Field()
    companyType=scrapy.Field()
    companyGeo=scrapy.Field()
    emplType=scrapy.Field()
    jobName=scrapy.Field()
    jobType0=scrapy.Field()
    jobType1=scrapy.Field()
    eduLevel=scrapy.Field()
    workingExp=scrapy.Field()
    salary=scrapy.Field()
    salary_down=scrapy.Field()
    salary_up=scrapy.Field()
    createDate=scrapy.Field()
    endDate=scrapy.Field()
    updateDate=scrapy.Field()
    timeState=scrapy.Field()
    jobCount=scrapy.Field()
    jobDesc=scrapy.Field()
    address=scrapy.Field()
