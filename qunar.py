# -*- coding:utf-8 -*-


import requests
import json

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
    'Cookie':'QN48=tc_fbc8381fb1f795d5_169f210d3ac_69b9;QN668=51%2C55%2C55%2C54%2C57%2C54%2C59%2C59%2C50%2C52%2C50%2C56%2C56;',
    #'Cookie':'QN48=tc_fbc8381fb1f795d5_169f210d3ac_69b9',
    '6975f6':'bec552ed45d2ce3d5404d2ed514ce02b',
}

url = 'https://flight.qunar.com/touch/api/domestic/wbdflightlist?departureCity=%E4%B8%8A%E6%B5%B7&arrivalCity=%E5%8C%97%E4%BA%AC&departureDate=2019-05-27'

url2 = 'https://m.flight.qunar.com/flight/api/touchInnerList'

headers2 = {
    'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
    'X-Requested-With':'XMLHttpRequest',
    #'Cookie':'QN48=854105ab-540c-470e-b430-7897bb2fc53f; QN668=51%2C55%2C55%2C54%2C58%2C58%2C50%2C55%2C54%2C54%2C51%2C59%2C57',
    #'a99e8f':'0506927586fefebbdfb10596f1c6164ccc503334',
}

data = {"arrCity":"上海",
        "baby":"0",
        "cabinType":"0",
        "child":"0",
        "depCity":"北京",
        "from":"touch_index_search",
        "goDate":"2019-04-11",
        "firstRequest":'true',
        "startNum":25,
        "sort":5,
        #"r":1554880834128,
        "_v":2,
        "underageOption":"",
        #"__m__":"c968c18fb85d219b4d6e1102127d118c"
}

res= requests.get(url,headers=headers)
print(json.loads(res.text))
result=json.loads(res.text)['data']['flights']

for i in result:
    print(i['code'],i['minPrice'])


