# -*- coding: utf-8 -*-

# Scrapy settings for xueqiu project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'xueqiu'

SPIDER_MODULES = ['xueqiu.spiders']
NEWSPIDER_MODULE = 'xueqiu.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'xueqiu (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 5

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 0.1
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
  'Host': 'xueqiu.com',
  'X-Requested-With': 'XMLHttpRequest',
  'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'xueqiu.middlewares.XueqiuSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   'xueqiu.middlewares.CookiesMiddleware': 555,
   'xueqiu.middlewares.AbuyunMiddleware' : 556,
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'xueqiu.pipelines.TimePipeline': 300,
   'xueqiu.pipelines.TypePipeline' : 301,
   'xueqiu.pipelines.MongoPipeline': 302,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'


#要做到中断后继续爬取，使用此命令运行爬虫,Request队列将被保存在某个路径下
#scrapy crawl spider -s JOB_DIR=crawls/spider

#要使用分布式的话将调度器的类和去重的类替换为scrapy-redis提供的类
#SCHEDULER = 'scrapy_redis.scheduler.Scheduler'
#DUPEFILTER_CLASS = 'scrapy_redis.dupefilter.RFPDupeFilter'
#配置redis连接,中括号代表密码选项可有可无，db是数据库代号，默认是0
#REDIS_URL = 'redis://@127.0.0.1:6379'
#配置调度队列(此配置是可选的，默认使用优先级队列）
#SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.PriorityQueue'
#SCHEDULER_QUEUE_CLASS = 'scrapy.redis.queue.FifoQueue'
#SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.LifoQueue'
#配置持久化(默认是False，会在爬取全部完成后清空请求队列和去重集合，不想的话则设置为True）
#SCHEDULER_PERSIST = True
#配置重爬(默认是False,爬虫启动时不会清空队列和集合，想清空则设置为True)
#SCHEDULER_FLUSH_ON_START = True
#配置Pipeline(默认不启动，启动的话会将生成的Item存储到redis数据库,一般不启动）
#ITEM_PIPELINES = {'scrapy_redis.pipelines.RedisPipeline':300}



#若要使用布隆过滤器请替换调度类和去重类
#SCHEDULER = "scrapy_redis_bloomfilter.scheduler.Scheduler"
#DUPEFILTER_CLASS = 'scrapy_redis_bloomfilter.dupefilter.RFPDupeFilter'
#散列函数的个数，默认为6，可以自行修改
#BLOOMFILTER_HASH_NUMBER = 6
#Bloom Filter的bit参数，默认30,去重数组占用128MB空间，去重量级1亿
#BLOOMFILTER_BIT = 30
#保留的日志等级
#LOG_LEVEL='INFO'

#DOWNLOAD_TIMEOUT=100

MONGO_URL='192.168.1.161'
MONGO_DB='XueQiuStock'
MONGO_PORT=27017

RETRY_ENABLED=True
RETRY_TIMES=20
RETRY_HTTP_CODES = [302, 400, 403, 408, 414, 500, 502, 503, 504]
COOKIES_URL='http://127.0.0.1:5555/xueqiu/random'
PROXY_URL='http://127.0.0.1:1080'
COOKIES=[{'xq_a_token':'33118214b9d3feaa92b82119cbe4953114dea3e8'}]


PROXYUSER="HP7Y01400L962MUD"
PROXYPASS="ED8926D78920DD44"
PROXYSERVER="http://http-dyn.abuyun.com:9020"