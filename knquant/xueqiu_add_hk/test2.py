# -*- coding:utf-8 -*-

import asyncio
import aiohttp
import time

start = time.time()









async def request():
    url = 'http://127.0.0.1:5000'
    print('Waiting for', url)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            print('Get response from', url, 'Result:', response.text)


tasks = [asyncio.ensure_future(request()) for _ in range(5)]
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.wait(tasks))

end = time.time()
print('Cost time:', end - start)