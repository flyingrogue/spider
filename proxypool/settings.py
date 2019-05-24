# _*_ coding:utf-8 _*_

#代理分数
MAX_SCORE=100
MIN_SCORE=0
INITIAL_SCORE=10

#redis数据库地址
REDIS_HOST='127.0.0.1'

#redis端口
REDIS_PORT=6379

#redis密码
REDIS_PASSWORD='kaina123'

#redis键名
REDIS_KEY='proxies'

#代理池数量界限
POOL_UPPER_THRESHOLD=10000

#有效状态码
VALID_STATUS_CODES=[200,]

#最大批测试量
BATCH_TEST_SIZE=10

#测试API,抓哪个网站测哪个
TEST_URL='https://xueqiu.com/v4/statuses/user_timeline.json?page=1&user_id=8205178197'

#测试周期
TESTER_CYCLE=10800

#获取周期
GETTER_CYCLE=10800

#开关
TESTER_ENABLED=True
GETTER_ENABLED=False
API_ENABLED=False

#API配置
API_HOST='127.0.0.1'
API_PORT=5000