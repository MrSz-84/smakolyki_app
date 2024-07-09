import re
import json
import requests
import aiohttp
import asyncio
import config.config as config
import utils.request_handling as req
import time


def main():
    start = time.time()
    with open(config.KEY, encoding='utf-8') as file:
        api_key = json.load(file)['Authorization']

    blog_id = req.input_blog_address()
    # blog_id = req.get_blog_id(address)
    url = req.return_request_url('by_id', blog_id=blog_id, auth=api_key,
                                 base_req_body=config.API_BASE_REQ)
    with requests.Session() as s:
        r = s.get(url)
        print(r.text)
    end = time.time()
    print(f'Elapsed: {end - start:.2f}')
    # blog = req.get_blog_id('smakolykibereniki.blogspot.com')
    # print(blog)


async def create_session():
    return aiohttp.ClientSession()


async def main2():
    start = time.time()
    with open(config.KEY, encoding='utf-8') as file:
        api_key = json.load(file)['Authorization']

    async with await req.ConnectionPool.get_session() as session:
        blog_id = await req.input_blog_address(session)



    end = time.time()
    print(f'Elapsed: {end - start:.2f}')


# TODO create tests for new functions: input_func, input_blog_address, validate_blog_name,
#  check_response_code, is_blogger, get_blog_id


if __name__ == '__main__':
    asyncio.run(main2())


