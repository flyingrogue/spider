# -*- coding:utf-8 -*-


import requests
import json
import time
import hashlib


headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
}

def getRandomKey(timestamp):
    n = "".join([str(ord(i)) for i in timestamp[4:]])
    m = hashlib.md5()
    m.update(n.encode("utf8"))
    result= m.hexdigest()
    return result[-6:]

def getRandomValue(timestamp, token):
    m = hashlib.md5()
    s = hashlib.sha1()
    if int(timestamp)%2 :
        m.update((token + timestamp).encode("utf8"))
        s.update(m.hexdigest().encode("utf8"))
        return s.hexdigest()
    else:
        s.update((token + timestamp).encode("utf8"))
        m.update(s.hexdigest().encode("utf8"))
        return m.hexdigest()



timestamp = str(int(time.time()*1000))

QN668 = "%2C".join([str(ord(i)+2) for i in timestamp])
QN48 = "tc_fbc8381fb1f795d5_169f210d3ac_69b9"

url = "https://flight.qunar.com/touch/api/domestic/wbdflightlist?departureCity=%E4%B8%8A%E6%B5%B7&arrivalCity=%E5%8C%97%E4%BA%AC&departureDate=2019-04-11"



headers.update({
    "Cookie": "QN48={QN48}; QN668={QN668};".format(QN48=QN48, QN668=QN668),
    "{}".format(getRandomKey(timestamp)): "{}".format(getRandomValue(timestamp, QN48))
})
#print(headers)
res = requests.get(url,headers=headers)
print(json.loads(res.text))
result = json.loads(res.text)['data']['flights'][0]
print(result)

