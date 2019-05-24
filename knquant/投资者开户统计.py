# -*- coding:utf-8 -*-

import requests
from requests.exceptions import ConnectionError,ConnectTimeout,Timeout
from urllib3.exceptions import NewConnectionError,MaxRetryError
from lxml import etree
#from locale import setlocale,LC_NUMERIC,atof
import calendar
import pymysql
import time
from datetime import datetime,date,timedelta
from dateutil.relativedelta import relativedelta

#一周投资者开户统计
def Weekdata(datestr):
    #setlocale(LC_NUMERIC, 'English_US')
    headers={
        'Host':'www.chinaclear.cn',
        'Referer':'http://www.chinaclear.cn/cms-search/view.action?action=china&viewType=&dateStr=&channelIdStr=',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
    }
    data={
        'dateType':'',
        'dateStr':datestr,
        'channelIdStr':'6ac54ce22db4474abc234d6edbe53ae7'
    }
    url='http://www.chinaclear.cn/cms-search/view.action?action=china'
    res=None
    while True:
        try:
            res=requests.post(url,data=data,headers=headers)
        except (TimeoutError,ConnectTimeout,ConnectionError,NewConnectionError,MaxRetryError) as e:
            print(e)
        if res:
            break
        else:
            time.sleep(2)
    html=etree.HTML(res.text)
    table=html.xpath('//*[@id="settlementList"]/table//tr/td//table')

    item={}
    if table:
        if table[0].xpath('.//tr[3]/td[2]/p/span//text()')[0]!='-':
            item['新增投资者数量_自然人']=float((table[0].xpath('.//tr[3]/td[2]/p/span//text()')[0]).replace(',',''))
        if table[0].xpath('.//tr[4]/td[2]/p/span//text()')[0]!='-':
            item['新增投资者数量_非自然人']=float((table[0].xpath('.//tr[4]/td[2]/p/span//text()')[0]).replace(',',''))
        item['期末投资者数量_自然人']=float((table[0].xpath('.//tr[6]/td[2]/p/span//text()')[0]).replace(',',''))
        item['期末投资者数量_自然人_已开立A股账户投资者']=float((table[0].xpath('.//tr[8]/td[2]/p/span//text()')[0]).replace(',',''))
        item['期末投资者数量_非自然人']=float((table[0].xpath('.//tr[10]/td[2]/p/span//text()')[0]).replace(',',''))
        item['期末投资者数量_非自然人_已开立A股账户投资者']=float((table[0].xpath('.//tr[12]/td[2]/p/span//text()')[0]).replace(',',''))

    return item

#一月信用账户开户统计
def Monthdata(year,month):
    #setlocale(LC_NUMERIC, 'English_US')
    headers = {
        'Host': 'www.chinaclear.cn',
        'Referer': 'http://www.chinaclear.cn/cms-search/monthview.action?action=china&channelFidStr=4f8a220e5ca04a388ca4bae0d1226d0d',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
    }
    data={
        'riqi':'{}年{}月'.format(year,month),
        'channelFidStr':'4f8a220e5ca04a388ca4bae0d1226d0d',
        'channelIdStr':'335db4403c8f45049a78a243550b0c44',
    }
    url='http://www.chinaclear.cn/cms-search/monthview.action?action=china'
    res=None
    while True:
        try:
            res=requests.post(url,data=data,headers=headers)
        except (TimeoutError,ConnectTimeout,ConnectionError,NewConnectionError,MaxRetryError) as e:
            print(e)
        if res:
            break
        else:
            time.sleep(2)
    html=etree.HTML(res.text)
    table=html.xpath('//*[@id="settlementList"]//table//tr/td/table')
    item = {}
    #print(table)
    if table:
        item['信用账户新增开户投资者数_合计'] = float((table[0].xpath('.//tr[5]/td[2]/p/span//text()')[0]).replace(',',''))
        item['信用账户新增开户投资者数_个人'] = float((table[0].xpath('.//tr[6]/td[2]/p/span//text()')[0]).replace(',',''))
        item['信用账户新增开户投资者数_机构'] = float((table[0].xpath('.//tr[7]/td[2]/p/span//text()')[0]).replace(',',''))
        item['信用账户新销账户投资者数_合计'] = float((table[0].xpath('.//tr[8]/td[2]/p/span//text()')[0]).replace(',',''))
        item['信用账户新销账户投资者数_个人'] = float((table[0].xpath('.//tr[9]/td[2]/p/span//text()')[0]).replace(',',''))
        item['信用账户新销账户投资者数_机构'] = float((table[0].xpath('.//tr[10]/td[2]/p/span//text()')[0]).replace(',',''))
        item['信用期末账户投资者数_合计'] = float((table[0].xpath('.//tr[11]/td[2]/p/span//text()')[0]).replace(',',''))
        item['信用期末账户投资者数_个人'] = float((table[0].xpath('.//tr[12]/td[2]/p/span//text()')[0]).replace(',',''))
        item['信用期末账户投资者数_机构'] = float((table[0].xpath('.//tr[13]/td[2]/p/span//text()')[0]).replace(',',''))
        #print(item)
    return item


MYSQL_HOST='192.168.1.161'
MYSQL_USER='quant'
MYSQL_PASSWORD='knquant123'
MYSQL_PORT=3306
MYSQL_DATABASE='test'

class Mysql():
    def __init__(self,host=MYSQL_HOST,username=MYSQL_USER,password=MYSQL_PASSWORD,port=MYSQL_PORT,
                 database=MYSQL_DATABASE):
        try:
            self.db=pymysql.connect(host,username,password,database,port=port)
            self.cursor=self.db.cursor()
        except pymysql.MySQLError as e:
            print(e.args)

    def insert(self,table,item):
        keys = ','.join(item.keys())
        values = ','.join(['%s'] * len(item))
        sql = 'INSERT INTO {table}({keys}) VALUES ({values}) ON DUPLICATE KEY UPDATE'.format(table=table, keys=keys,
                                                                                             values=values)
        update = ','.join([" {key} = %s".format(key=key) for key in item])
        sql = sql + update
        try:
            if self.cursor.execute(sql, tuple(item.values()) * 2):
                print('Sucessful')
                self.db.commit()
        except:
            print('Failed')
            self.db.rollback()

    def insert2(self,table,item):
        keys = ','.join(item.keys())
        values = ','.join(['%s'] * len(item))
        sql="insert into {table} ({keys}) values ({values}) where not exists (select * from {table} where Date='{date}')".format(
            table=table,keys=keys,values=values,date=item['Date']
        )
        #try:
        self.cursor.execute(sql, tuple(item.values()))
        #print('Sucessful')
        self.db.commit()
        # except:
        #     print('Failed')
        #     self.db.rollback()

    def __del__(self):
        self.db.close()


def main(year,month,mysql):
    # 获得一个月的所有周五
    c = calendar.Calendar(firstweekday=calendar.SUNDAY)
    monthcal = c.monthdatescalendar(year, month)
    fridays = [day for week in monthcal for day in week if day.weekday() == calendar.FRIDAY and day.month == month]
    for friday in fridays:
        datestr=str(friday).replace('-','.')
        # 获取每周数据
        weekitem=Weekdata(datestr)
        if weekitem:
            weekitem['Date']=friday
            # if friday==fridays[-1]:
            #     temp=datestr.split('.')
            #     monthitem=Monthdata(temp[0],temp[1])
            #     if monthitem:
            #         for key,value in monthitem.items():
            #             weekitem[key]=value
            print(weekitem)
            mysql.insert('投资者开户统计',weekitem)
        time.sleep(2)

    first_day=date(year,month,1)
    temp=str(first_day).split('-')
    # 获取每月数据
    monthitem=Monthdata(temp[0],temp[1])
    if monthitem:
        # 加上月底那天的日期
        daynum=calendar.monthrange(year,month)[1]
        last_day=first_day+timedelta(daynum-1)
        monthitem['Date']=last_day
        print(monthitem)
        mysql.insert('投资者开户统计', monthitem)

if __name__=='__main__':
    while True:
        now=datetime.now()
        if now.hour in [12,16,17] and now.minute in [00,30]:
            mysql=Mysql()
            # 从上月开始更新
            datetime_start = date.today() - relativedelta(months=1)
            for i in range(2):
                temp = str(datetime_start).split('-')
                main(int(temp[0]),int(temp[1]),mysql)
                datetime_start = datetime_start + relativedelta(months=1)
            # for i in range(1,11):
            #     main(2018,i,mysql)
        time.sleep(60)