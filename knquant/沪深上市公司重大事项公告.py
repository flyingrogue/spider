# -*- coding: utf-8 -*-


import requests
from lxml import etree
import pymysql
import re
import time
from datetime import datetime

url='http://stock.eastmoney.com/a/cwjkx.html'
index_url='http://stock.eastmoney.com/a/cwjkx_{}.html'

headers={
    #'Host':'stock.eastmoney.com',
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
}
HOST1='192.168.1.161'
HOST2='192.168.1.208'
USER='quant'
PASSWORD1='knquant123'
PASSWORD2='knquant@99'
PORT=3306
DATABASSE1='test'
DATABASSE2='wind'

class Message():
    def __init__(self,host1=HOST1,host2=HOST2,user=USER,password1=PASSWORD1,password2=PASSWORD2,db1=DATABASSE1,db2=DATABASSE2,port=PORT):
        self.db1=pymysql.connect(host1,user,password1,database=db1,port=port)
        self.db2=pymysql.connect(host2,user,password2,database=db2,port=port)
        self.cursor1=self.db1.cursor()
        self.cursor2=self.db2.cursor()

    def __del__(self):
        self.db1.close()
        self.db2.close()

    def insert(self,item):
        #从wind获取股票代码添加到item中
        sql2 = 'select S_INFO_WINDCODE from ASHAREDESCRIPTION where S_INFO_NAME="{}"'
        self.cursor2.execute(sql2.format(item['Name']))
        code = self.cursor2.fetchone()
        if code:
            item['Code'] = code[0]
        #将item插入mysql
        keys = ','.join(item.keys())
        values = ','.join(['%s'] * len(item))
        sql='insert into 沪深上市公司重大事项公告 ({keys}) VALUES ({values}) ON DUPLICATE KEY UPDATE'.format(keys=keys,values=values)
        update = ','.join([" {key} = %s".format(key=key) for key in item])
        sql = sql + update
        try:
            if self.cursor1.execute(sql, tuple(item.values()) * 2):
                print('Sucessful')
                self.db1.commit()
        except:
            print('Failed')
            self.db1.rollback()


    def parse_detail(self,url):
        res=requests.get(url,headers=headers)
        res.encoding='utf8'
        #print(res.text)
        html=etree.HTML(res.text)
        #获取公告发表日期
        date_time=html.xpath('//*[@class="newsContent"]//div[@class="time"]/text()')[0]
        date_time=datetime.strptime(date_time,'%Y年%m月%d日 %H:%M')
        #获取公告URL后面的一串数字再加上每条数据所处行数，形成每条数据的ID
        content_id=re.findall('.*?(20\d+).html',url)[0]
        p=html.xpath('//*[@id="ContentBody"]/p')
        pattern=re.compile('【(\D+)】')
        #外循环遍历每个P节点，找到分类标志【】，再内循环遍历接下来的节点，遇到分类标志则结束内循环，继续进行外循环
        for i in range(len(p)):
            texts=p[i].xpath('.//text()')
            temp=''.join(texts).strip()
            text_type=re.findall(pattern,temp)
            if text_type:
                #for j in range(i+1,len(p),2):
                j=i+1
                while j<len(p):
                    if re.findall(pattern,''.join(p[j].xpath('.//text()')).strip()):
                        break
                    else:
                        mes=re.split('：|:',''.join(p[j].xpath('.//text()')).strip())
                        #遇到一些特定文本，则说明到了页尾，结束内循环
                        if mes[0] in ['(责任编辑','','炒股大赛>>>']:
                            break
                        content = ''.join(p[j + 1].xpath('.//text()')).strip()
                        #有些正文上面有一行空白，则要跳过
                        if content=='':
                            content=''.join(p[j + 2].xpath('.//text()')).strip()
                            j+=1
                        if re.match('[\w(]{2,6}：|:.*',content):
                            break
                        #有些标题前没有冒号，无法分割得到股票名字，则根据下面的正文获取
                        if len(mes)>1:
                            ticker_name=mes[0]
                            title=mes[1]
                        else:
                            ticker_name=''
                            for a,b in zip(list(mes[0]),list(content)):
                                if a==b:
                                    ticker_name+=a
                                else:
                                    break
                            title = mes[0]

                        # if p[j].xpath('.//a'):
                        #     ticker_code=re.findall('.*com.*?(\d+)\.html',p[j].xpath('.//a[1]/@href')[0])[0]
                        # else:
                        #     ticker_code=re.findall('.*com.*?(\d+)\.html',p[j+1].xpath('.//a[1]/@href')[0])[0]
                        #print(datetime,content_id+str(j),text_type[0],ticker_name,title,content)
                        yield {
                            'Datetime':date_time,
                            'Content_type':text_type[0],
                            'Name':ticker_name,
                            'Title':title,
                            'Content':content,
                            'Content_id':content_id+str(j)
                        }
                    j+=2


    def main(self):
        for page in range(1,2):
            res=requests.get(index_url.format(page))
            html=etree.HTML(res.text)
            detail_urls = html.xpath('//*[@id="newsListContent"]/li/div/p[@class="title"]/a/@href')
            for i in range(1):
                for result in self.parse_detail(detail_urls[i]):
                    print(result)
                    self.insert(result)
            time.sleep(2)


if __name__=='__main__':
    while True:
        now = datetime.now()
        if now.hour in [17,18,19] and now.minute in [15,25,35]:
            mess=Message()
            mess.main()
        time.sleep(60)
    #mess.parse_detail('http://stock.eastmoney.com/a/20180903938953927.html')