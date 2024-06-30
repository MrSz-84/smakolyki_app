import re
import json
import requests
import config.config as config
import utils.request_handling as req
import time


def main():
    start = time.time()
    with open(config.KEY, encoding='utf-8') as file:
        api_key = json.load(file)['Authorization']

    # url = req.return_request_url('by_id', blog_id=config.BLOG_ID, auth=api_key,
    #                              base_req_body=config.API_BASE_REQ)

    # blog, user = req.get_blog_and_user_id(config.BLOG_URL)

    address = req.input_blog_address()
    is_blogger = req.is_blogger(address)
    if is_blogger:
        blog_id = req.get_blog_id(address)
        url = req.return_request_url('by_id', blog_id=blog_id, auth=api_key,
                                     base_req_body=config.API_BASE_REQ)
        r = requests.get(url)
        print(r.text)
    end = time.time()
    print(f'Elapsed: {end - start:.2f}')
    # blog = req.get_blog_id('smakolykibereniki.blogspot.com')
    # print(blog)

# TODO create tests for new functions: input_func, input_blog_address, validate_blog_name,
#  check_response_code, is_blogger, get_blog_id


if __name__ == '__main__':
    main()
