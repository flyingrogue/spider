# -*- coding:utf-8 -*-

from requests import Session
from requests import Request
from requests import ConnectionError,ReadTimeout
from queue import Queue
import redis
from pickle import dumps,loads
from threading import Thread,Lock
import json
from lxml import etree
import pymongo
import time

TIMEOUT=15
MAX_FAILED_TIME=5

MONGO_HOST='192.168.1.161'
MONGO_PORT=27017
MONGO_DB='testdump'

REDIS_HOST='localhost'
REDIS_PORT=6379
REDIS_PASSWORD=None
REDIS_KEY='zhilian'

CRAWL_EXIT=False
PROXYHOST = "http-dyn.abuyun.com"
PROXYPORT = "9020"
PROXYUSER = "HP7Y01400L962MUD"
PROXYPASS = "ED8926D78920DD44"
COUNT=0
FLAG=3571

#自定义请求
class ZhilianRequest(Request):
    def __init__(self,url,callback,method='GET',headers=None,need_proxy=False,fail_time=0,timeout=TIMEOUT,meta={}):
        #注意此处三个参数顺序不能写错,或者写成url=url的形式
        Request.__init__(self,method,url,headers)
        self.callback=callback
        self.need_proxy=need_proxy
        self.fail_time=fail_time
        self.timeout=timeout
        self.meta=meta

# class RedisQueue():
#     #初始化Redis
#     def __init__(self):
#         self.db=redis.StrictRedis(host=REDIS_HOST,port=REDIS_PORT,password=REDIS_PASSWORD)
#
#     #向队列添加序列化后的Request
#     def add(self,request):
#         if isinstance(request,ZhilianRequest):
#             return self.db.rpush(REDIS_KEY,dumps(request))
#         return False
#
#     #取出下一个Request并反序列化
#     def pop(self):
#         if self.db.llen(REDIS_KEY):
#             return loads(self.db.lpop(REDIS_KEY))
#         return False
#
#     def empty(self):
#         return self.db.llen(REDIS_KEY)==0

class MongoDB():
    def __init__(self,host=MONGO_HOST,port=MONGO_PORT,database=MONGO_DB):
        self.host=host
        self.port=port
        self.database=database
        self.client=pymongo.MongoClient(host=self.host,port=self.port)
        self.auth = self.client.admin
        self.auth.authenticate('spyder', 'knquant123')
        self.db=self.client[self.database]
        self.stocks=self.get_stocks()

    def __del__(self):
        self.client.close()

    def get_stocks(self):
        stocks={}
        with open('/home/jbliu/projects/stockname.txt','r',encoding='utf-8') as f:
            for temp in eval(f.read()):
                stocks[temp[:-8]]=temp[-8:]
        return stocks

    def create_collection(self):
        print(len(self.stocks.values()))
        for code in self.stocks.values():
            self.db[code].create_index([('jobId',pymongo.DESCENDING)])

    def insert(self,item,name):
        self.db[self.stocks[name]].update({'jobId': dict(item).get('jobId')}, {'$set': item}, True)

#定义采集线程
class CrawlThread(Thread):
    def __init__(self,threadName,requestQueue,session,mongo):
        super(CrawlThread,self).__init__()
        self.threadName=threadName
        self.requestQueue=requestQueue
        self.session=session
        self.mongo=mongo

    #线程启动
    def run(self):
        print(self.threadName,'启动')
        while not CRAWL_EXIT:
            try:
                zhilian_request=self.requestQueue.get(False)
                callback=zhilian_request.callback
                start=zhilian_request.meta.get('start')
                kw=zhilian_request.meta.get('kw')
                response=self.send_request(zhilian_request)
                if response and response.status_code==200:
                    results=list(callback(response,start,kw))
                    #print(results)
                    if results:
                        for result in results:
                            if isinstance(result,ZhilianRequest):
                                self.requestQueue.put(result)
                            if isinstance(result,dict):
                                self.mongo.insert(result,kw)

                else:
                    self.error(zhilian_request)
                    print(response.url,response.status_code)
            except:
                pass
        print(self.threadName,'结束')

    #执行请求
    def send_request(self, zhilian_request):
        try:
            if zhilian_request.need_proxy:
                proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
                    "host": PROXYHOST,
                    "port": PROXYPORT,
                    "user": PROXYUSER,
                    "pass": PROXYPASS,
                }
                proxies = {
                    "http": proxyMeta,
                    "https": proxyMeta,
                }
                return self.session.send(zhilian_request.prepare(),
                                         timeout=zhilian_request.timeout, allow_redirects=False, proxies=proxies)
            return self.session.send(zhilian_request.prepare(), timeout=zhilian_request.timeout, allow_redirects=False)
        except (ConnectionError, ReadTimeout) as e:
            print(e.args)
            return False

    #错误处理
    def error(self,zhilian_request):
        zhilian_request.fail_time += 1
        print('Request Failed',zhilian_request.fail_time,'Times',zhilian_request.url)
        if zhilian_request.fail_time < MAX_FAILED_TIME:
            self.requestQueue.put(zhilian_request)


class Spider():
    base_url = 'https://fe-api.zhaopin.com/c/i/sou?start={start}&pageSize=90&cityId=489&workExperience=-1&education=-1&' \
               'companyType=-1&employmentType=-1&jobWelfareTag=-1&kw={kw}&kt=2'
    headers = {
        'Host': 'fe-api.zhaopin.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    }
    session=Session()
    queue=Queue()
    lock=Lock()
    mongo=MongoDB()

    #解析索引页
    def parse_index(self,response,start,kw):
        text=json.loads(response.text)
        results=text['data']['results']
        num = int(text['data']['numFound'])
        if results:
            for result in results:
                item={}
                item['jobId']=result['number']
                item['applyType']=int(result['applyType'])
                item['city']=result['city']['display']
                item['companyName']=result['company']['name']
                item['companyType']=result['company']['type']['name']
                item['companyGeo']=result['geo']
                item['emplType']=result['emplType']
                item['jobName']=result['jobName']
                temp=result['jobType']['display'].split(',')
                for i in range(len(temp)):
                    item['jobType{}'.format(i)]=temp[i]
                item['eduLevel']=result['eduLevel']['name']
                item['workingExp']=result['workingExp']['name']
                item['salary']=result['salary']
                item['createDate']=result['createDate']
                item['endDate']=result['endDate']
                item['updateDate']=result['updateDate']
                item['timeState']=result['timeState']
                item['jobCount']=''
                item['jobDesc']=''
                item['address']=''
                yield item
                if int(result['applyType'])==1:
                    url='https://jobs.zhaopin.com/{}.htm'.format(result['number'])
                    yield ZhilianRequest(url=url,callback=self.parse_detail,meta={'start':start,'kw':kw})
                else:
                    url='https://xiaoyuan.zhaopin.com/job/{}'.format(result['number'])
                    yield ZhilianRequest(url=url,callback=self.parse_school,meta={'start': start, 'kw': kw})

        if num>(start+90):
            start+=90
            yield ZhilianRequest(url=self.base_url.format(start=start,kw=kw),callback=self.parse_index,meta={'start':start,'kw':kw},need_proxy=False)
        else:
            self.lock.acquire()
            global FLAG
            FLAG-=1
            self.lock.release()

    #解析普通招聘详情页
    def parse_detail(self,response,start,kw):
        jobId=response.url.split('/')[3].split('.')[0]
        html=etree.HTML(response.text)
        count=html.xpath('//*[@class="main"]/div[4]/div/ul/li[2]/div[2]/span[4]//text()')
        if count:
            jobCount=int(count[0][1])
        else:
            jobCount=''
        jobDesc = ''.join(html.xpath('//*[@class="main"]//div[@class="pos-ul"]//text()')).strip()
        add=html.xpath('//*[@class="main"]//p[@class="add-txt"]//text()')
        if add:
            address=add[0]
        else:
            address=''
        yield {
            'jobId':jobId,
            'jobCount':jobCount,
            'jobDesc':jobDesc,
            'address':address
        }

    #解析校园招聘详情页
    def parse_school(self,response,start,kw):
        jobId = response.url.split('/')[4]
        html = etree.HTML(response.text)
        count=html.xpath('//*[@id="divMain"]//div[@class="cJobDetailInforWrap"]/ul[2]/li[6]//text()')
        if count:
            jobCount=count[0]
        else:
            jobCount=''
        jobDesc=''.join(html.xpath('//*[@id="divMain"]//div[@class="cJob_Detail f14"]/p//text()')).strip()
        add=html.xpath('//*[@id="jobCompany"]/a//text()')
        if add:
            address=add[0]
        else:
            address=''
        yield {
            'jobId':jobId,
            'jobCount':jobCount,
            'jobDesc':jobDesc,
            'address':address
        }


    # 初始化工作
    def start_requests(self):
        # 全局更新headers
        self.session.headers.update(self.headers)
        self.mongo.create_collection()
        for key in self.mongo.get_stocks().keys():
            zhilian_request = ZhilianRequest(url=self.base_url.format(start=0, kw=key), callback=self.parse_index,
                                             meta={'start': 0, 'kw': key}, need_proxy=False)
            self.queue.put(zhilian_request)

    def main(self):
        start_time=time.time()
        crawllist = ['采集线程1号','采集线程2号','采集线程3号','采集线程4号','采集线程5号','采集线程6号','采集线程7号','采集线程8号']
        crawlthread = []
        for threadName in crawllist:
            thread = CrawlThread(threadName, self.queue, self.session, self.mongo)
            thread.start()
            crawlthread.append(thread)

        #time.sleep(60)
        global FLAG
        while FLAG>0:
            pass
        #time.sleep(5)
        while not self.queue.empty():
            pass
        global CRAWL_EXIT
        CRAWL_EXIT = True
        print('queue为空')
        for thread in crawlthread:
            thread.join()
        print('爬取全部完成')
        end_time=time.time()
        print(end_time-start_time)


if __name__=='__main__':
    spider=Spider()
    spider.start_requests()
    spider.main()