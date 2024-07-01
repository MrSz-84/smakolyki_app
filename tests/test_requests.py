import pytest
import json
import sys
from config import config as cnf
from utils import request_handling as req


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
    url = cnf.BASE_BLOG_URL
    body = cnf.API_BASE_REQ
    by_url_result = f'{cnf.API_BASE_REQ}byurl?url={cnf.BASE_BLOG_URL}?key={api_key}'
    assert req.return_request_url(req_type=request, auth=api_key, base_req_body=body,
                                  blog_url=url) == by_url_result
    request = 'by_url'
    url = 'foobazbar'
    body = cnf.API_BASE_REQ
    by_url_result = f'{cnf.API_BASE_REQ}byurl?url={cnf.BASE_BLOG_URL}?key={api_key}'
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


def test_check_input_func(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: 'this is test text')
    assert req.input_func() == 'this is test text'
    monkeypatch.setattr('builtins.input', lambda _: 'some blog name here')
    assert req.input_func() == 'some blog name here'
    assert req.input_func() != 'foobarbaz'


def test_raise_error_input_func(monkeypatch):
    monkeypatch.setattr(sys.stdin, 'readline', lambda: 'foo')
    with pytest.raises(AssertionError):
        assert req.input_func() == 'foobar'
    monkeypatch.setattr(req, 'input_func', lambda: '')
    with pytest.raises(AssertionError):
        assert req.input_func() == '1'


def test_input_blog_address_goes_towards_validation(monkeypatch):
    valid = 'learningpythonway'
    invalid = 'http://foobar.blogspot.com'
    user_inputs = iter([invalid, invalid, invalid, valid])

    def mock_input_func():
        return next(user_inputs)

    def mock_validate_blog_name(name):
        return name == valid

    def mock_check_response_code(name):
        return name == valid

    monkeypatch.setattr('utils.request_handling.input_func', mock_input_func)
    monkeypatch.setattr('utils.request_handling.validate_blog_name', mock_validate_blog_name)
    monkeypatch.setattr('utils.request_handling.check_response_code', mock_check_response_code)

    assert req.input_blog_address() == f'https://{valid}.blogspot.com/'


def test_input_blog_address_raises_runtime(monkeypatch):
    valid = 'learningpythonway'
    invalid = 'http://foobar.blogspot.com'
    user_inputs = iter([invalid, invalid, invalid])

    def mock_input_func():
        return next(user_inputs)

    def mock_validate_blog_name(name):
        return name == valid

    def mock_check_response_code(name):
        return name == valid

    monkeypatch.setattr('utils.request_handling.input_func', mock_input_func)
    monkeypatch.setattr('utils.request_handling.validate_blog_name', mock_validate_blog_name)
    monkeypatch.setattr('utils.request_handling.check_response_code', mock_check_response_code)

    with pytest.raises(StopIteration):
        assert req.input_blog_address()

# TODO make assertion to what the function prints to the stdout,
#  what would simulate the False response from validating functions capsys.stdouterr()


