

import requests

headers={
    #'Host':'xueqiu.com',
    #'Referer': 'https://xueqiu.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
}

res=requests.get('https://xueqiu.com/',headers=headers)
print(res.cookies)