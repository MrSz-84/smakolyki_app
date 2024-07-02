import re
import json
import requests
import config.config as cnf
import utils.various as various


def input_func():
    the_input = input('Type in blog`s name: ')
    if len(the_input) == 0:
        the_input = cnf.BASE_BLOG_NAME
    return the_input


def input_blog_address():
    print('What blog hosted on Blogger would you like to see? Omit .blogspot.com and http parts.')
    blog_name = input_func()
    ok_name = False
    ok_conn = False
    while not ok_name and not ok_conn:
        ok_name = validate_blog_name(blog_name)
        if not ok_name:
            print('Inputted value contains more than blog`s name.')
            blog_name = input_func()
            continue
        ok_conn = check_response_code(blog_name)
        if not ok_conn:
            print('Requested blog seems to not respond, try one more time.')
            blog_name = input_func()
            ok_name = False
    blog_url = f'https://{blog_name}.blogspot.com/'
    return blog_url


def validate_blog_name(name):
    user_input = name.lower().strip()
    hits = re.compile(r'^https\D{3}|^http\D{3}|\Dblogspot|\Dblogger|\Dcom|\Dcom$|/$')
    if not bool(re.search(hits, user_input)):
        print('Name Valid')
        return True
    else:
        print('Name Invalid')
        return False


def check_response_code(to_check):
    url = f'https://{to_check}.blogspot.com/'
    try:
        with requests.get(url, stream=True) as r:
            if r.status_code == 200:
                print('Connection Valid')
                return True
            else:
                print('Connection Invalid')
                return False
    except (requests.ConnectionError, requests.exceptions.InvalidURL):
        print('Connection Error')
        return False


def is_blogger(url):
    with requests.get(url, stream=True) as r:
        link = re.compile(r'.blogger.com/')
        generator = re.compile(r"<meta content='blogger' name='generator'/>")
        feed = re.compile(r'/feeds/posts/default')
        blogger_in_link = False
        blogger_as_generator = False
        feed_in_link = False
        for chunk in r.iter_content(chunk_size=1024, decode_unicode=True):
            if not isinstance(link, re.Match):
                blogger_in_link = bool(re.search(link, chunk))
            if not isinstance(generator, re.Match):
                blogger_as_generator = bool(re.search(generator, chunk))
            if not isinstance(feed, re.Match):
                feed_in_link = bool(re.search(feed, chunk))
            if all([blogger_in_link, blogger_as_generator, feed_in_link]):
                return True


def get_blog_id(url):
    blog_pattern = re.compile(r'blog-([0-9]*)<', re.I)
    blogger = re.compile(r'tag:blogger.com')
    # user_pattern = re.compile(r'profile/([0-9]*)<', re.I)
    blog_id = ''
    url = f'{url}/feeds/posts/default'
    with requests.get(url, stream=True) as r:
        for chunk in r.iter_content(chunk_size=1600, decode_unicode=True):
            if not isinstance(blogger, re.Match):
                blogger = re.search(blogger, chunk)
            if not isinstance(blog_id, re.Match):
                blog_id = re.search(blog_pattern, chunk)
            if blog_id is not None:
                return blog_id.group(1)


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
