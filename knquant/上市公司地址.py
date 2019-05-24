# -*- coding:utf-8 -*-

import requests
import json
from urllib.parse import urlencode
import pymysql
import time
from datetime import datetime

def getlnglat(address):
    base_url = 'http://api.map.baidu.com/geocoder/v2/?'
    ak = '2U9UhaUBPVE8cuM3wAgvhMO6G9WjVpHR'
    params = {
        'address': address,
        'output': 'json',
        'ak': ak
    }
    url = base_url + urlencode(params)
    res = requests.get(url)
    temp = json.loads(res.text)
    return temp

MYSQL_HOST='192.168.1.208'
MYSQL_USER='quant'
MYSQL_PASSWORD='knquant@99'
MYSQL_PORT=3306
MYSQL_DATABASE1='wind'
MYSQL_DATABASE2='test'

class Mysql():
    def __init__(self,host=MYSQL_HOST,username=MYSQL_USER,password=MYSQL_PASSWORD,port=MYSQL_PORT,
                 database1=MYSQL_DATABASE1,database2=MYSQL_DATABASE2):
        try:
            self.db1=pymysql.connect(host,username,password,database=database1,port=port)
            self.db2 = pymysql.connect(host, username, password, database=database2, port=port)
            self.cursor1=self.db1.cursor()
            self.cursor2=self.db1.cursor()
            self.cursor3 = self.db2.cursor()
            self.cursor4 = self.db2.cursor()
        except pymysql.MySQLError as e:
            print(e.args)

    def getlnglat(self,address):
        base_url = 'http://api.map.baidu.com/geocoder/v2/?'
        ak = '2U9UhaUBPVE8cuM3wAgvhMO6G9WjVpHR'
        params = {
            'address': address,
            'output': 'json',
            'ak': ak
        }
        url = base_url + urlencode(params)
        res = requests.get(url)
        temp = json.loads(res.text)
        return temp

    #更新HKCOMPANYINFO的经纬度
    def main1(self):
        count=0
        sql1='select OBJECT_ID,OFFICE from HKCOMPANYINFO'
        sql2='update HKCOMPANYINFO set LONGITUDE=%s,LATITUDE=%s where OBJECT_ID=%s'
        try:
            self.cursor1.execute(sql1)
            row=self.cursor1.fetchone()
            while row:
                if row[1]:
                    count += 1
                    temp=self.getlnglat(row[1])
                    if temp['status']==0:
                        lng=temp['result']['location']['lng']
                        lat=temp['result']['location']['lat']
                        try:
                            if self.cursor2.execute(sql2,(lng,lat,row[0])):
                                print('Successful')
                                self.db1.commit()
                        except:
                            print('Failed')
                            self.db1.rollback()
                row=self.cursor1.fetchone()
                #time.sleep(0.2)
            print(count)
        except pymysql.Error as e:
            print(e.args)

    #检查wind.COMPINTRODUCTION中是否增加了上市公司，是则插入test
    def main2(self):
        sql1='select OBJECT_ID,COMP_ID,COMP_NAME,COMP_SNAME,PROVINCE,CITY,ADDRESS,OFFICE,OPDATE from COMPINTRODUCTION where IS_LISTED=1'
        sql2='select * from COMPINTRODUCTION where OBJECT_ID="{}"'
        sql3='insert into COMPINTRODUCTION (OBJECT_ID,COMP_ID,COMP_NAME,COMP_SNAME,PROVINCE,CITY,ADDRESS,OFFICE,OPDATE,LONGITUDE,LATITUDE) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        try:
            self.cursor1.execute(sql1)
            row=self.cursor1.fetchone()
            while row:
                self.cursor3.execute(sql2.format(row[0]))
                id = self.cursor3.fetchone()
                if not id:
                    print(row[2])
                    temp = self.getlnglat(row[6])
                    if temp['status']==0:
                        lng=temp['result']['location']['lng']
                        lat=temp['result']['location']['lat']
                        try:
                            if self.cursor3.execute(sql3, (
                            row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8],lng,lat)):
                                print('Successful', row)
                                self.db2.commit()
                        except:
                            print('Failed')
                            self.db2.rollback()
                row = self.cursor1.fetchone()
        except pymysql.Error as e:
            print(e.args)

    #检查wind.COMPINTRODUCTION中公司地址是否有变动，变动则更新test中地址及其经纬度
    def main3(self):
        sql1='select OBJECT_ID,ADDRESS,OPDATE from COMPINTRODUCTION'
        sql2='select COMP_NAME,COMP_SNAME,PROVINCE,CITY,ADDRESS,OFFICE,OPDATE from COMPINTRODUCTION where OBJECT_ID=%s'
        sql3='update COMPINTRODUCTION set COMP_NAME=%s,COMP_SNAME=%s,PROVINCE=%s,CITY=%s,ADDRESS=%s,OFFICE=%s,OPDATE=%s where OBJECT_ID=%s'
        sql4='update COMPINTRODUCTION set LONGITUDE=%s,LATITUDE=%s where OBJECT_ID=%s'
        try:
            self.cursor3.execute(sql1)
            row=self.cursor3.fetchone()
            while row:
                self.cursor1.execute(sql2,(row[0]))
                data=self.cursor1.fetchone()
                #判断操作时间是否变化，变化则更新公司基本信息
                if row[2]!=data[6]:
                    print('操作时间变化',row)
                    try:
                        if self.cursor4.execute(sql3,(data[0],data[1],data[2],data[3],data[4],data[5],data[6],row[0])):
                            print('Successful')
                            self.db2.commit()
                    except:
                        print('Failed')
                        self.db2.rollback()
                    #判断公司地址是否变化，变化则更新经纬度
                    if row[1]!=data[4]:
                        print('此地址发生变化',row)
                        temp=self.getlnglat(data[4])
                        if temp['status'] == 0 and temp['result']['precise']==1:
                            lng = temp['result']['location']['lng']
                            lat = temp['result']['location']['lat']
                            try:
                                if self.cursor4.execute(sql4, (lng, lat, row[0])):
                                    print('Successful')
                                    self.db2.commit()
                            except:
                                print('Failed')
                                self.db2.rollback()

                row=self.cursor3.fetchone()
                #time.sleep(0.2)

        except pymysql.Error as e:
            print(e.args)

    # 检查wind.HKCOMPANYINFO中公司地址是否有变动，变动则更新test中地址及其经纬度
    def main4(self):
        sql1 = 'select OBJECT_ID,OFFICE,OPDATE from HKCOMPANYINFO'
        sql2 = 'select S_INFO_COMPCODE,S_INFO_COMPNAME,ADDRESS,OFFICE,COUNTRY,OPDATE from HKCOMPANYINFO where OBJECT_ID=%s'
        sql3 = 'update HKCOMPANYINFO set S_INFO_COMPCODE=%s,S_INFO_COMPNAME=%s,ADDRESS=%s,OFFICE=%s,COUNTRY=%s,OPDATE=%s where OBJECT_ID=%s'
        sql4 = 'update HKCOMPANYINFO set LONGITUDE=%s,LATITUDE=%s where OBJECT_ID=%s'
        try:
            self.cursor3.execute(sql1)
            row = self.cursor3.fetchone()
            while row:
                self.cursor1.execute(sql2, (row[0]))
                data = self.cursor1.fetchone()
                # 判断操作时间是否变化，变化则更新公司基本信息
                if row[2] != data[5]:
                    print('操作时间变化', row)
                    try:
                        if self.cursor4.execute(sql3, (
                                data[0], data[1], data[2], data[3], data[4], data[5], row[0])):
                            print('Successful')
                            self.db2.commit()
                    except:
                        print('Failed')
                        self.db2.rollback()
                    # 判断公司地址是否变化，变化则更新经纬度
                    if row[1] != data[3]:
                        print('此地址发生变化', row)
                        temp = self.getlnglat(data[3])
                        if temp['status'] == 0 and temp['result']['precise'] == 1:
                            lng = temp['result']['location']['lng']
                            lat = temp['result']['location']['lat']
                            try:
                                if self.cursor4.execute(sql4, (lng, lat, row[0])):
                                    print('Successful')
                                    self.db2.commit()
                            except:
                                print('Failed')
                                self.db2.rollback()

                row = self.cursor3.fetchone()
                # time.sleep(0.2)

        except pymysql.Error as e:
            print(e.args)

    def __del__(self):
        self.db1.close()
        self.db2.close()

if __name__=='__main__':
    #print(getlnglat('北京市海淀区高梁桥斜街59号院1号楼16层1606'))
    while True:
        now=datetime.now()
        if now.hour==11:
            mysql=Mysql()
            mysql.main2()
        if now.hour==12:
            mysql=Mysql()
            mysql.main3()
        time.sleep(3600)
