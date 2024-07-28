import re
import json
import requests
import aiohttp
import asyncio
import config.config as config
import utils.request_handling as req
import time


async def main():
    start = time.time()
    with open(config.KEY, encoding='utf-8') as file:
        api_key = json.load(file)['Authorization']

    async with await req.ConnectionPool.get_session() as session:
        blog_id = False
        while not blog_id:
            blog_id = await req.input_blog_address(session)
        blog_info = await req.extract_blog_info(api_key, blog_id, session)
        print(json.dumps(blog_info, indent=2, ensure_ascii=False))
        posts_info = await req.extract_posts_info(api_key, blog_id, session)
        # print(json.dumps(posts_info, indent=2, ensure_ascii=False))
        print(len(posts_info))


    end = time.time()
    print(f'Elapsed: {end - start:.2f}')


if __name__ == '__main__':
    asyncio.run(main(), debug=True)

