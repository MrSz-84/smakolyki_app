import pytest
import json
from config import config as cnf
from utils import requests as req


with open(cnf.KEY, encoding='utf-8') as file:
    api_key = json.load(file)['Authorization']

test_requests = {
    'by_url': 'https://www.googleapis.com/blogger/v3/blogs/byurl?url=None?key=None',
    'by_id': 'https://www.googleapis.com/blogger/v3/blogs/None?key=None',
    'posts': 'https://www.googleapis.com/blogger/v3/blogs/None/posts?key=None',
    'post': 'https://www.googleapis.com/blogger/v3/blogs/None/posts/None?key=None',
    'search': 'https://www.googleapis.com/blogger/v3/blogs/None/posts/search?q=None&key=None',
    'by_path': 'https://www.googleapis.com/blogger/v3/blogs/None/posts/bypath?path=None&key=None',
    'comments': 'https://www.googleapis.com/blogger/v3/blogs/None/posts/None/comments?key=None'
}


def test_validate_error_message_key_present():
    requests = test_requests.copy()
    request = 'by_id'
    assert req.validate_error_message(request, requests) is True
    request = 'by_url'
    assert req.validate_error_message(request, requests) is True
    request = 'posts'
    assert req.validate_error_message(request, requests) is True
    request = 'search'
    assert req.validate_error_message(request, requests) is True
    request = 'by_path'
    assert req.validate_error_message(request, requests) is True
    request = 'comments'
    assert req.validate_error_message(request, requests) is True


def test_validate_error_message_key_absent():
    requests = test_requests.copy()
    request = 'by_by'
    assert req.validate_error_message(request, requests) is False
    request = 'foo'
    assert req.validate_error_message(request, requests) is False
    request = 'bar'
    assert req.validate_error_message(request, requests) is False
    request = 'i hate python`s path management'
    assert req.validate_error_message(request, requests) is False


def test_req_types_return():
    request = 'by_id'
    id_ = cnf.BLOG_ID
    body = cnf.API_BASE_REQ
    by_id_result = f'https://www.googleapis.com/blogger/v3/blogs/{cnf.BLOG_ID}?key={api_key}'
    assert req.return_request_url(req_type=request, blog_id=id_, auth=api_key,
                                  base_req_body=body) == by_id_result
    request = 'by_url'
    url = cnf.BLOG_URL
    body = cnf.API_BASE_REQ
    by_url_result = f'{cnf.API_BASE_REQ}byurl?url={cnf.BLOG_URL}?key={api_key}'
    assert req.return_request_url(req_type=request, auth=api_key, base_req_body=body,
                                  blog_url=url) == by_url_result
    request = 'by_url'
    url = 'foobazbar'
    body = cnf.API_BASE_REQ
    by_url_result = f'{cnf.API_BASE_REQ}byurl?url={cnf.BLOG_URL}?key={api_key}'
    assert req.return_request_url(req_type=request, auth=api_key, base_req_body=body,
                                  blog_url=url) != by_url_result


def test_req_types_return_exception_raising():
    with pytest.raises(ValueError):
        request = 'foobar'
        id_ = cnf.BLOG_ID
        body = cnf.API_BASE_REQ
        by_id_result = f'https://www.googleapis.com/blogger/v3/blogs/{cnf.BLOG_ID}?key={api_key}'
        assert req.return_request_url(req_type=request, blog_id=id_, auth=api_key,
                                      base_req_body=body)
    with pytest.raises(ValueError):
        request = 'by_id'
        body = cnf.API_BASE_REQ
        by_id_result = f'https://www.googleapis.com/blogger/v3/blogs/{cnf.BLOG_ID}?key={api_key}'
        assert req.return_request_url(req_type=request, auth=api_key,
                                      base_req_body=body)
