# -*- coding:utf-8 -*-

import requests
from datetime import datetime,date,timedelta
from dateutil.relativedelta import relativedelta
import time
import pymysql




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


    def __del__(self):
        self.db.close()

def main(year,mon,mysql):
    for item in Shibor(year, mon):
        if item:
            #将'Date'字段转换为date格式
            temp=item['Date'].split('-')
            item['Date']=date(int(temp[0]),int(temp[1]),int(temp[2]))
            print(item)
            #将item插入mysql
            mysql.insert('SHIBOR', item)

if __name__=='__main__':
    while True:
        now=datetime.now()
        if now.hour in [11] and now.minute in range(5):
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