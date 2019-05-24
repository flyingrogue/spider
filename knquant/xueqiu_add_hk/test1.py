# -*- coding:utf-8 -*-

import requests
from lxml import etree
import json
headers={
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
}
url='https://fe-api.zhaopin.com/c/i/sou?start=180&pageSize=90&cityId=489&workExperience=-1&education=-1&companyType=-1&employmentType=-1&jobWelfareTag=-1&kw=%E6%8B%9B%E5%95%86%E9%93%B6%E8%A1%8C&kt=2'
url1='https://xiaoyuan.zhaopin.com/job/CC000114437J90000001000'
response=requests.get(url1,headers=headers)
# results=json.loads(response.text)['data']['results']
# print(len(results))

#html=etree.HTML(response.text)
# jobCount=html.xpath('//*[@class="main"]/div[4]/div/ul/li[2]/div[2]/span[4]//text()')[0]
# jobDesc=''.join(html.xpath('//*[@class="main"]//div[@class="pos-ul"]//text()')).strip()
#
# address=html.xpath('//*[@class="main"]//p[@class="add-txt"]//text()')
# print(jobCount,jobDesc,address)
html=etree.HTML(response.text)
jobId = response.url.split('/')[4]
jobCount=html.xpath('//*[@id="divMain"]//div[@class="cJobDetailInforWrap"]/ul[2]/li[6]//text()')[0]
jobDesc=''.join(html.xpath('//*[@id="divMain"]//div[@class="cJob_Detail f14"]/p//text()')).strip()
address=html.xpath('//*[@id="jobCompany"]/a//text()')[0]

print(jobId,jobCount,jobDesc,address)