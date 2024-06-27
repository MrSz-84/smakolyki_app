import config.config as config
import json


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


def validate_error_message(request, requests):
    if request not in requests.keys():
        return False
    else:
        try:
            none_present = 'None' in requests.get(request)
        except TypeError:
            return False
    return none_present


with open(config.KEY, encoding='utf-8') as file:
    auth_ = json.load(file)['Authorization']
API_BASE_REQ = 'https://www.googleapis.com/blogger/v3/blogs/'
BLOG_ID = '3417787614555634377'
BLOG_URL = 'https://smakolykibereniki.blogspot.com/'


# return_request_url(req_type='', base_req_body=API_BASE_REQ)
aaa = return_request_url(req_type='by_url', auth=auth_, blog_url=BLOG_URL, base_req_body=API_BASE_REQ)
print(aaa)


# TODO create test for this function: return_request_url()
