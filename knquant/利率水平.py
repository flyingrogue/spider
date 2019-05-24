# -*- coding:utf-8 -*-

import requests
from requests.exceptions import ConnectionError,ConnectTimeout,Timeout
from urllib3.exceptions import NewConnectionError,MaxRetryError
from lxml import etree
import json
import time
from datetime import datetime,date,timedelta
from dateutil.relativedelta import relativedelta
import pymysql

#抓取国债数据
def Chinabond(datetime):
    headers={
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
        'Host':'yield.chinabond.com.cn',
        'Origin':'http://yield.chinabond.com.cn',
        'X-Requested-With':'XMLHttpRequest',
        'Referer':'http://yield.chinabond.com.cn/cbweb-mn/yield_main',
        #'Cookie':'JSESSIONID=0000P6Cf0-Ufk8X4DDVpDeSa10h:-1',
    }
    table_url='http://yield.chinabond.com.cn/cbweb-mn/yc/ycDetail?ycDefIds=2c9081e50a2f9606010a3068cae70001&&zblx=txy&&workTime={datetime}&&dxbj=0&&qxlx=0,&&yqqxN=N&&yqqxK=K&&wrjxCBFlag=0&&locale=zh_CN'.format(datetime=datetime)
    json_url='http://yield.chinabond.com.cn/cbweb-mn/yc/searchYc?xyzSelect=txy&&workTimes={datetime}&&dxbj=0&&qxll=0,&&yqqxN=N&&yqqxK=K&&ycDefIds=2c9081e50a2f9606010a3068cae70001,&&wrjxCBFlag=0&&locale=zh_CN'.format(datetime=datetime)

    item={}
    bond_item={}
    field_map={
        '中债国债到期收益率_0年':'0.0y','中债国债到期收益率_1个月':'0.08y','中债国债到期收益率_2个月':'0.17y','中债国债到期收益率_3个月':'0.25y',
        '中债国债到期收益率_6个月':'0.5y','中债国债到期收益率_9个月':'0.75y','中债国债到期收益率_1年':'1.0y','中债国债到期收益率_2年':'2.0y',
        '中债国债到期收益率_3年': '3.0y','中债国债到期收益率_4年':'4.0y','中债国债到期收益率_5年':'5.0y','中债国债到期收益率_6年':'6.0y',
        '中债国债到期收益率_7年': '7.0y','中债国债到期收益率_8年':'8.0y','中债国债到期收益率_9年':'9.0y','中债国债到期收益率_10年':'10.0y',
        '中债国债到期收益率_15年': '15.0y','中债国债到期收益率_20年':'20.0y','中债国债到期收益率_30年':'30.0y','中债国债到期收益率_40年':'40.0y',
        '中债国债到期收益率_50年': '50.0y',
    }

    table_res = None
    while True:
        try:
            table_res = requests.post(table_url, headers=headers, timeout=5)
            # print(table_res.status_code)
        except (TimeoutError,ConnectTimeout,ConnectionError,NewConnectionError,MaxRetryError) as e:
            print(e)
        if table_res:
            break
        else:
            time.sleep(2)
    html=etree.HTML(table_res.text)
    table=html.xpath('//*[@class="tablelist"]')
    if table:
        for i in range(2,len(table[0].xpath('./tr'))+1):
            item[table[0].xpath('./tr[{}]/td[1]/text()'.format(i))[0]]=float(table[0].xpath('./tr[{}]/td[2]/text()'.format(i))[0])
    json_res = None
    while True:
        try:
            json_res = requests.post(json_url, headers=headers, timeout=5)
            # print(json_res.status_code)
        except (TimeoutError,ConnectTimeout,ConnectionError,NewConnectionError,MaxRetryError) as e:
            print(e)
        if json_res:
            break
        else:
            time.sleep(2)
    if json_res.text:
        result=json.loads(json_res.text)
        seriesData=result[0]['seriesData']
        for series in seriesData:
            if series[0] in [2,4,6,8,9]:
                item[str(series[0])+'y']=series[1]
    if item:
        for field,key in field_map.items():
            if key in item.keys():
                bond_item[field]=item[key]

    return bond_item

#抓取Shibor数据
def Shibor(year,mon):
    url = 'http://www.shibor.org/shibor/web/html/downLoad.html?nameNew=Historical_Shibor_Data_{year}_{mon}.txt&downLoadPath=data'.format(year=year,mon=mon)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
        'Referer': 'http://www.shibor.org/shibor/web/downLoad.jsp',
        'Host': 'www.shibor.org',
    }
    res = requests.get(url, headers=headers)
    #print(res.status_code)
    temp = res.text.split('\n')

    item = {}
    for i in range(2, len(temp) - 1):
        item['Date'] = temp[i][0:10]
        item['SHIBOR_隔夜'] = float(temp[i][15:21])
        item['SHIBOR_1周'] = float(temp[i][26:32])
        item['SHIBOR_2周'] = float(temp[i][39:45])
        item['SHIBOR_1个月'] = float(temp[i][51:57])
        item['SHIBOR_3个月'] = float(temp[i][63:69])
        item['SHIBOR_6个月'] = float(temp[i][75:81])
        item['SHIBOR_9个月'] = float(temp[i][87:93])
        item['SHIBOR_1年'] = float(temp[i][99:105])
        yield item




MYSQL_HOST='192.168.1.161'
MYSQL_USER='quant'
MYSQL_PASSWORD='knquant123'
MYSQL_PORT=3306
MYSQL_DATABASE='MacroDB'

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

def main(year,mon,mysql):
    for shibor_item in Shibor(year, mon):
        if shibor_item:
            item={}
            #将shibor数据插入item
            for key,value in shibor_item.items():
                item[key]=value
            #根据shibor的日期抓取那天的国债数据，插入item
            bond_item = Chinabond(shibor_item['Date'])
            if bond_item:
                for key, value in bond_item.items():
                    item[key] = value
            #将'Date'字段转换为date格式
            temp=item['Date'].split('-')
            item['Date']=date(int(temp[0]),int(temp[1]),int(temp[2]))
            print(item)
            #将item插入mysql
            mysql.insert('利率水平2', item)
            

if __name__=='__main__':
    while True:
        now=datetime.now()
        if now.hour in [11,18] and now.minute in [5,10]:
            mysql=Mysql()
            datetime_start = date.today()
            temp = str(datetime_start).split('-')
            main(int(temp[0]), int(temp[1]), mysql)
            #从当前月份的上个月开始更新
            # datetime_start=date.today()-relativedelta(months=1)
            # for i in range(2):
            #     temp=str(datetime_start).split('-')
            #     main(int(temp[0]),int(temp[1]),mysql)
            #     datetime_start = datetime_start + relativedelta(months=1)
        time.sleep(60)

    # CURRENTMONTH='2018-10'
    # traverseDay = date(int(CURRENTMONTH[0:4]), int(CURRENTMONTH[5:7]), 1)
    # intMonth = int(CURRENTMONTH[5:7])
    # while True:
    #     if intMonth == traverseDay.month:
    #         datetime=traverseDay.strftime('%Y-%m-%d')
    #         item=Chinabond(datetime)
    #         if item:
    #             item['Date']=traverseDay
    #             print(item)
    #         traverseDay = traverseDay + timedelta(days=1)
    #     else:
    #         break
