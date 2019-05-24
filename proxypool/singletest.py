# _*_ coding:utf-8 _*_

import requests


def main():
    headers={
             'Host':'xueqiu.com',
             'Referer':'https://xueqiu.com/u/8205178197',
             'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
             'X-Requested-With':'XMLHttpRequest',
             'Cookie':'device_id=5d27463e2df6a534e7ecba029eb95e29; xq_a_token=f89219d7e7ee863a5773244ad9d2db6e3dc5ea38; xq_r_token=8bdf53186f54b2c5c885621e64fd4d728f3111e0;',
            }
    url='https://xueqiu.com/v4/statuses/user_timeline.json?page=1&user_id=8205178197'
    proxy='110.85.89.87:37473'

    proxies={
        'http':'http://'+proxy,
        'https':'https://'+proxy
    }
    try:
        res=requests.get(url,headers=headers,proxies=proxies)
        print(res.text)
    except Exception as e:
        print('Error:',e.args)


if __name__=="__main__":
    main()