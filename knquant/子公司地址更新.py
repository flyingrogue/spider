# -*- coding: utf-8 -*-

import requests
from requests.exceptions import ConnectionError,ConnectTimeout,Timeout
import pymysql
import pymongo
import json
from urllib.parse import urlencode
import re
import time

MYSQL_HOST='192.168.1.208'
MYSQL_USER='quant'
MYSQL_PASSWORD='knquant@99'
MYSQL_PORT=3306
MYSQL_DATABASE='test'
MONGO_URL='192.168.1.99'
MONGO_DB='Patent'
MONGO_COLLECTION='Patent_info_raw4'
MONGO_PORT=27017
HOLDSHARE='ASHARECOMPANYHOLDSHARES_18down'

class Company():
    def __init__(self,host=MYSQL_HOST,username=MYSQL_USER,password=MYSQL_PASSWORD,port=MYSQL_PORT,database=MYSQL_DATABASE,
                 mongo_url=MONGO_URL,mongo_db=MONGO_DB,mongo_port=MONGO_PORT,mongo_collection=MONGO_COLLECTION):

        self.db=pymysql.connect(host,username,password,database=database,port=port)
        self.cursor1=self.db.cursor()
        self.cursor2=self.db.cursor()

        self.client = pymongo.MongoClient(host=mongo_url, port=mongo_port)
        self.collection=self.client[mongo_db][mongo_collection]

    def getlnglat(self,address):
        base_url = 'http://api.map.baidu.com/geocoder/v2/?'
        ak = '2U9UhaUBPVE8cuM3wAgvhMO6G9WjVpHR'
        params = {
            'address': address,
            'output': 'json',
            'ak': ak
        }
        url = base_url + urlencode(params)
        res=None
        while True:
            try:
                res=requests.get(url)
            except ConnectTimeout or ConnectionError or Timeout as e:
                print(e)
            if res:
                break
            else:
                time.sleep(2)
        return json.loads(res.text)


    def main(self):
        count1=0
        count2=0
        sql1='select S_CAPITALOPERATION_COMPANYNAME from {}'.format(HOLDSHARE)
        sql2='update {} set ADDRESS=%s,LONGITUDE=%s,LATITUDE=%s where S_CAPITALOPERATION_COMPANYNAME=%s'.format(HOLDSHARE)
        self.cursor1.execute(sql1)
        row=self.cursor1.fetchone()
        while row:
            count1+=1
            if count1>=0:
                com_name=row[0]
                if re.match('.*\(.*\).*',row[0]):
                    a=row[0].replace('(','（')
                    com_name=a.replace(')','）')
                results = self.collection.find({'Applicant1': {'$in':[row[0],com_name]}})
                addresses = []
                for result in results:
                    if result['Applicant1'][0] == row[0] or result['Applicant1'][0]==com_name:
                        addresses.append(re.findall('.*?([^0-9].*)', result['ApplicantAddress'][0])[0])
                if addresses:
                    num = [len(i) for i in addresses]
                    address = addresses[num.index(max(num))]
                    # print(address)
                    temp = self.getlnglat(address)
                    if temp['status'] == 0:
                        lng = temp['result']['location']['lng']
                        lat = temp['result']['location']['lat']
                        try:
                            if self.cursor2.execute(sql2, (address,lng, lat, row[0])):
                                #print('Successful')
                                count2+=1
                                print('已更新',count2)
                                self.db.commit()
                        except:
                            print('Failed')
                            self.db.rollback()
            row=self.cursor1.fetchone()
            print('总计',count1)

    def __del__(self):
        self.db.close()
        self.client.close()

if __name__=='__main__':
    company=Company()
    company.main()