# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from zhilian.items import JobItem
from lxml import etree
import json
import numpy as np
import re

class ZhaopinSpider(scrapy.Spider):
    name = 'zhaopin'
    allowed_domains = ['zhaopin.com']

    sou_url = 'https://fe-api.zhaopin.com/c/i/sou?start={start}&pageSize=90&cityId=489&workExperience=-1&education=-1&' \
               'companyType=-1&employmentType=-1&jobWelfareTag=-1&kw={kw}&kt=2'
    jobs_url='https://jobs.zhaopin.com/{}.htm'
    school_url='https://xiaoyuan.zhaopin.com/job/{}'

    def start_requests(self):
        with open('/home/jbliu/projects/zhilian/stockname.txt','r',encoding='utf8') as f:
            for temp in eval(f.read()):
                kw=temp[:-8]
                code=temp[-8:]
                yield Request(self.sou_url.format(start=0,kw=kw),callback=self.parse_index,meta={'start':0,'kw':kw,'code':code},dont_filter=True)
            print('@'*100)
        npy=np.load('/home/jbliu/projects/zhilian/holdshare.npy')
        for i in range(len(npy)):
            kw=npy[i][:-8]
            code=npy[i][-8:]
            yield Request(self.sou_url.format(start=0,kw=kw),callback=self.parse_index,meta={'start':0,'kw':kw,'code':code},dont_filter=True)
        print('@'*100)


    #解析索引页
    def parse_index(self, response):
        start=response.meta.get('start')
        kw=response.meta.get('kw')
        code=response.meta.get('code')
        if re.match('{.*}',response.text,re.S):
            text = json.loads(response.text)
            results = text['data']['results']
            num = int(text['data']['numFound'])
            if results:
                job_item=JobItem()
                for result in results:
                    job_item['jobId'] = result['number']
                    job_item['applyType'] = int(result['applyType'])
                    job_item['city'] = result['city']['display']
                    job_item['companyName'] = result['company']['name']
                    job_item['companyType'] = result['company']['type']['name']
                    job_item['companyGeo'] = result['geo']
                    job_item['emplType'] = result['emplType']
                    job_item['jobName'] = result['jobName']
                    temp = result['jobType']['display'].split(',')
                    job_item['jobType0'] = temp[0]
                    if len(temp)>1:
                        job_item['jobType1'] = temp[1]
                    job_item['eduLevel'] = result['eduLevel']['name']
                    job_item['workingExp'] = result['workingExp']['name']
                    job_item['salary'] = result['salary']
                    if len(result['salary'].split('-'))==2 and len(result['salary'].split('.'))<2:
                        job_item['salary_down']=int(result['salary'].split('-')[0][:-1])
                        job_item['salary_up'] = int(result['salary'].split('-')[1][:-1])
                    job_item['createDate'] = result['createDate']
                    job_item['endDate'] = result['endDate']
                    job_item['updateDate'] = result['updateDate']
                    job_item['timeState'] = result['timeState']
                    job_item['collection']=code
                    yield job_item

                    if int(result['applyType']) == 1:
                        yield Request(url=self.jobs_url.format(result['number']), callback=self.parse_detail, meta={'start': start, 'kw': kw ,'code':code},
                                      dont_filter=True)
                    else:
                        yield Request(url=self.school_url.format(result['number']), callback=self.parse_school, meta={'start': start, 'kw': kw, 'code':code},
                                      dont_filter=True)

            if num > (start + 90):
                start += 90
                req=Request(url=self.sou_url.format(start=start, kw=kw), callback=self.parse_index,
                                     meta={'start': start, 'kw': kw, 'code':code},dont_filter=True)
                req.meta['retry_times']=1
                yield req
        else:
            req=Request(url=self.sou_url.format(start=start,kw=kw),callback=self.parse_index,
                          meta={'start': start, 'kw': kw, 'code':code},dont_filter=True)
            req.meta['retry_times'] = 1
            yield req

    #解析普通招聘详情页
    def parse_detail(self, response):
        code=response.meta.get('code')
        job_item = JobItem()
        job_item['collection'] = code
        job_item['jobId']=response.url.split('/')[3].split('.')[0]
        html = etree.HTML(response.text)
        count = html.xpath('//*[@class="main"]/div[4]/div/ul/li[2]/div[2]/span[4]//text()')
        if count:
            job_item['jobCount'] = int(count[0][1])
        job_item['jobDesc'] = ''.join(html.xpath('//*[@class="main"]//div[@class="pos-ul"]//text()')).strip()
        add = html.xpath('//*[@class="main"]//p[@class="add-txt"]//text()')
        if add:
            job_item['address'] = add[0]
        yield job_item

    #解析校园招聘详情页
    def parse_school(self,response):
        code = response.meta.get('code')
        job_item=JobItem()
        job_item['collection'] = code
        job_item['jobId'] = response.url.split('/')[4]
        html = etree.HTML(response.text)
        count=html.xpath('//*[@id="divMain"]//div[@class="cJobDetailInforWrap"]/ul[2]/li[6]//text()')
        if count:
            job_item['jobCount']=count[0]
        job_item['jobDesc']=''.join(html.xpath('//*[@id="divMain"]//div[@class="cJob_Detail f14"]/p//text()')).strip()
        add=html.xpath('//*[@id="jobCompany"]/a//text()')
        if add:
            job_item['address']=add[0]
        yield job_item