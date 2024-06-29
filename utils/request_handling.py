import re
import json
import requests
import config.config as config


def return_request_url(req_type, blog_url=None, blog_id=None, post_id=None, auth=None, phrase=None,
                       post_path=None, base_req_body=''):
    # for post_path use such structure "YYYY/MM/post-title.html" for instance
    # "/2011/08/latest-updates-august-1st.html"
    # base_req_body = 'https://www.googleapis.com/blogger/v3/blogs/'
    req_types = {
        'by_url': f'{base_req_body}byurl?url={blog_url}?key={auth}',
        'by_id': f'{base_req_body}{blog_id}?key={auth}',
        'posts': f'{base_req_body}{blog_id}/posts?key={auth}',
        'post': f'{base_req_body}{blog_id}/posts/{post_id}?key={auth}',
        'search': f'{base_req_body}{blog_id}/posts/search?q={phrase}&key={auth}',
        'by_path': f'{base_req_body}{blog_id}/posts/bypath?path={post_path}&key={auth}',
        'comments': f'{base_req_body}{blog_id}/posts/{post_id}/comments?key={auth}',
    }
    none_val_in_req = validate_error_message(req_type, req_types)
    if req_type not in req_types.keys() or 'None' in req_types.get(req_type):
        raise ValueError(f'Variable req_type not included in possible requests: '
                         f'{req_type not in req_types}, \nor variables needed for request creation '
                         f'are missing: {none_val_in_req}')
    else:
        return req_types.get(req_type)


def validate_error_message(request, requests_pool):
    if request not in requests_pool.keys():
        return False
    else:
        try:
            none_present = 'None' in requests_pool.get(request)
        except TypeError:
            return False
    return none_present


def get_blog_id(url):
    blog_pattern = re.compile(r'blog-([0-9]*)<', re.I)
    blogger = re.compile(r'tag:blogger.com')
    # user_pattern = re.compile(r'profile/([0-9]*)<', re.I)
    blog_id = ''
    url = f'https://{url}/feeds/posts/default'
    with requests.get(url, stream=True) as r:
        for chunk in r.iter_content(chunk_size=1600, decode_unicode=True):
            if not isinstance(blogger, re.Match):
                blogger = re.search(blogger, chunk)
                print(blogger)
                exit()
            if not isinstance(blog_id, re.Match):
                blog_id = re.search(blog_pattern, chunk)
            if blog_id is not None:
                return blog_id.group(1)






def is_blogger(url):
    ...