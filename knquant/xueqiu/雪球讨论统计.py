# -*- coding: utf-8 -*-

import requests
from requests.exceptions import ProxyError
from urllib3.exceptions import MaxRetryError
import json
import pymysql
import time
from datetime import datetime
import re

HOST='192.168.1.161'
USER='quant'
PASSWORD='knquant123'
PORT=3306
DATABASSE='test'

proxyHost = "http-dyn.abuyun.com"
proxyPort = "9020"
proxyUser = "HP7Y01400L962MUD"
proxyPass = "ED8926D78920DD44"

class Mysql():
    def __init__(self,host=HOST,user=USER,password=PASSWORD,db=DATABASSE,port=PORT):
        self.db=pymysql.connect(host,user,password,database=db,port=port)
        self.cursor=self.db.cursor()


    def __del__(self):
        self.db.close()

    def crawl(self):
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://xueqiu.com/hq/screener',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
            'Cookie': 'xq_a_token=243bb1cce89c8d4d365a26452e50d6e62b83db37;',
        }
        url = 'https://xueqiu.com/stock/screener/screen.json?category=SH&exchange=&areacode=&indcode=&orderby=symbol&order=desc&current=ALL&pct=ALL&' \
              'page={}&follow=87_956021&follow7d=0_4073&tweet=12_214438&tweet7d=0_3470&deal=0_3203&deal7d=0_21'
        proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
            "host": proxyHost,
            "port": proxyPort,
            "user": proxyUser,
            "pass": proxyPass,
        }
        proxies = {
            "http": proxyMeta,
            "https": proxyMeta,
        }
        for page in range(1,121):
            res=None
            while True:
                try:
                    # sess=requests.session()
                    # first=sess.get(base_url,headers=headers,proxies=proxies,timeout=5)
                    res = requests.get(url.format(page), headers=headers, proxies=proxies, timeout=5)
                except (OSError,MaxRetryError,ProxyError) as e:
                    pass
                if res and re.match('{.*?"list".*}', res.text, re.S):
                    break

            results=json.loads(res.text).get('list')
            #print(page)
            for result in results:
                    item={}
                    item['symbol']=result.get('symbol')
                    item['sname'] = result.get('name')
                    item['follow']=int(result.get('follow'))
                    item['follow7d'] = int(result.get('follow7d'))
                    item['tweet'] = int(result.get('tweet'))
                    item['tweet7d'] = int(result.get('tweet7d'))
                    item['deal']=int(result.get('deal'))
                    item['deal7d']=int(result.get('deal7d'))
                    yield item

    def main(self):
        cntime = time.strftime('%Y-%m-%d', time.localtime(int(str(time.time())[:10])))
        sql1='create table if not exists `{}`(id int(11) NOT NULL AUTO_INCREMENT,symbol varchar(20) DEFAULT NULL,sname varchar(20) DEFAULT NULL,follow int(11) DEFAULT NULL,follow7d int(11) DEFAULT NULL,tweet int(11) DEFAULT NULL,tweet7d int(11) DEFAULT NULL,deal int(11) DEFAULT NULL,deal7d int(11) DEFAULT NULL,PRIMARY KEY (id))ENGINE=InnoDB DEFAULT CHARSET=utf8'
        sql2='insert into `{}`(symbol,sname,follow,follow7d,tweet,tweet7d,deal,deal7d) values (%s,%s,%s,%s,%s,%s,%s,%s)'
        self.cursor.execute(sql1.format('雪球讨论统计'+cntime))
        for item in self.crawl():
            try:
                self.cursor.execute(sql2.format('雪球讨论统计'+cntime),tuple(item.values()))
                self.db.commit()
            except pymysql.Error as e:
                self.db.rollback()
                print(e.args)


if __name__=='__main__':
    mysql=Mysql()
    mysql.main()