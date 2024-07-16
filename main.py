import re
import json
import requests
import aiohttp
import asyncio
import config.config as config
import utils.request_handling as req
import time


async def main2():
    start = time.time()
    with open(config.KEY, encoding='UTF-8') as file:
        api_key = json.load(file)['Authorization']

    async with await req.ConnectionPool.get_session() as session:
        blog_id = await req.input_blog_address(session)
        print('blog id: ', blog_id)



    end = time.time()
    print(f'Elapsed: {end - start:.2f}')


# TODO check how to catch errors from aiohttp or asyncio,
#  while other libraries return exceptions


if __name__ == '__main__':
    asyncio.run(main2(), debug=True)


# async def main3():
#     async with aiohttp.ClientSession() as session:
#         async with session.get('https://googlevideo87263e987?.gog.pl?)__+)L!@*&(') as resp:
#             print(resp.status)
#             print(await resp.text())
#
# asyncio.run(main3())
