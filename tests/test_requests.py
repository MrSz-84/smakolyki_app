import pytest
import json
import sys
import requests_mock
import requests
import asyncio
import aiohttp
from aiohttp import web

import utils.request_handling
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
    'comments': 'https://www.googleapis.com/blogger/v3/blogs/None/posts/None/comments?key=None',
}


def test_validate_error_message_key_present():
    request_type = test_requests.copy()
    request = 'by_id'
    assert (
        req.validate_error_message(request, request_type) is True
    ), 'should be True but was False'
    request = 'by_url'
    assert (
        req.validate_error_message(request, request_type) is True
    ), 'should be True but was False'
    request = 'posts'
    assert (
        req.validate_error_message(request, request_type) is True
    ), 'should be True but was False'
    request = 'search'
    assert (
        req.validate_error_message(request, request_type) is True
    ), 'should be True but was False'
    request = 'by_path'
    assert (
        req.validate_error_message(request, request_type) is True
    ), 'should be True but was False'
    request = 'comments'
    assert (
        req.validate_error_message(request, request_type) is True
    ), 'should be True but was False'


def test_validate_error_message_key_absent():
    request_type = test_requests.copy()
    request = 'by_by'
    assert (
        req.validate_error_message(request, request_type) is False
    ), 'should be False but was True'
    request = 'foo'
    assert (
        req.validate_error_message(request, request_type) is False
    ), 'should be False but was True'
    request = 'bar'
    assert (
        req.validate_error_message(request, request_type) is False
    ), 'should be False but was True'
    request = 'i hate python`s path management'
    assert (
        req.validate_error_message(request, request_type) is False
    ), 'should be False but was True'


def test_req_types_return():
    request = 'by_id'
    id_ = cnf.BLOG_ID
    body = cnf.API_BASE_REQ
    by_id_result = (
        f'https://www.googleapis.com/blogger/v3/blogs/{cnf.BLOG_ID}?key={api_key}'
    )
    assert (
        req.return_request_url(
            req_type=request, blog_id=id_, auth=api_key, base_req_body=body
        )
        == by_id_result
    )
    request = 'by_url'
    url = cnf.BASE_BLOG_URL
    body = cnf.API_BASE_REQ
    by_url_result = f'{cnf.API_BASE_REQ}byurl?url={cnf.BASE_BLOG_URL}?key={api_key}'
    assert (
        req.return_request_url(
            req_type=request, auth=api_key, base_req_body=body, blog_url=url
        )
        == by_url_result
    )
    request = 'by_url'
    url = 'foobazbar'
    body = cnf.API_BASE_REQ
    by_url_result = f'{cnf.API_BASE_REQ}byurl?url={cnf.BASE_BLOG_URL}?key={api_key}'
    assert (
        req.return_request_url(
            req_type=request, auth=api_key, base_req_body=body, blog_url=url
        )
        != by_url_result
    )


def test_req_types_return_exception_raising():
    with pytest.raises(ValueError):
        request = 'foobar'
        id_ = cnf.BLOG_ID
        body = cnf.API_BASE_REQ
        assert req.return_request_url(
            req_type=request, blog_id=id_, auth=api_key, base_req_body=body
        )
    with pytest.raises(ValueError):
        request = 'by_id'
        body = cnf.API_BASE_REQ

        assert req.return_request_url(
            req_type=request, auth=api_key, base_req_body=body
        )


def test_check_input_func(monkeypatch):
    """
    Test function that simulates inputs given by the user.
    :param monkeypatch: Pytest's built-in fixture
    :return: None
    """
    monkeypatch.setattr('builtins.input', lambda _: 'this is test text')
    assert req.input_func() == 'this is test text'
    monkeypatch.setattr('builtins.input', lambda _: 'some blog name here')
    assert req.input_func() == 'some blog name here'
    assert req.input_func() != 'foobarbaz'


def test_raise_error_input_func(monkeypatch):
    """
    Test function that simulates inputs given by the user. Tests exceptions raising.
    :param monkeypatch: Pytest's built-in fixture
    :return: None
    """

    monkeypatch.setattr(sys.stdin, 'readline', lambda: 'foo')
    with pytest.raises(AssertionError):
        assert req.input_func() == 'foobar'
    monkeypatch.setattr(req, 'input_func', lambda: '')
    with pytest.raises(AssertionError):
        assert req.input_func() == '1'


@pytest.mark.asyncio
async def test_input_blog_address_goes_towards_validation(monkeypatch):
    """
    Test for simulating user inputs ending with positive input and assertion
    :param monkeypatch: Pytest's built-in fixture
    :return: None
    """
    valid = 'learningpythonway'
    invalid = 'http://foobar.blogspot.com'
    user_inputs = iter([invalid, invalid, invalid, valid])
    valid_url = f'https://{valid}.blogspot.com/'
    id = '12345'

    def mock_input_func():
        return next(user_inputs)

    async def mock_validate_blog_name(name):
        return name == valid

    async def mock_check_response_code(name, session):
        return name == valid

    async def mock_is_blogger(url, session):
        return url == valid_url

    async def mock_get_blog_id(url, session):
        if url == valid_url:
            return id
        return False

    async with aiohttp.ClientSession() as session:
        monkeypatch.setattr('utils.request_handling.input_func', mock_input_func)
        monkeypatch.setattr('utils.request_handling.validate_blog_name', mock_validate_blog_name)
        monkeypatch.setattr('utils.request_handling.check_response_code', mock_check_response_code)
        monkeypatch.setattr('utils.request_handling.is_blogger', mock_is_blogger)
        monkeypatch.setattr('utils.request_handling.get_blog_id', mock_get_blog_id)

        assert await req.input_blog_address(session) == '12345'


@pytest.mark.asyncio
async def test_input_blog_address_raises_runtime(monkeypatch):
    """
    Test for simulating user inputs, ending with no valid input and exception raising
    :param monkeypatch: Pytest's built-in fixture
    :return: None
    """
    valid = 'learningpythonway'
    invalid = 'http://foobar.blogspot.com'
    user_inputs = iter([invalid, invalid, invalid, invalid])
    valid_url = f'https://{valid}.blogspot.com/'
    id = '12345'

    def mock_input_func():
        return next(user_inputs)

    async def mock_validate_blog_name(name):
        return name == valid

    async def mock_check_response_code(name, session):
        return name == valid

    async def mock_is_blogger(url, session):
        if url == valid_url:
            return True
        return False

    async def mock_get_blog_id(url, session):
        if url == valid_url:
            return id
        return False

    async with aiohttp.ClientSession() as session:
        monkeypatch.setattr('utils.request_handling.input_func', mock_input_func)
        monkeypatch.setattr('utils.request_handling.validate_blog_name', mock_validate_blog_name)
        monkeypatch.setattr('utils.request_handling.check_response_code', mock_check_response_code)
        monkeypatch.setattr('utils.request_handling.is_blogger', mock_is_blogger)
        monkeypatch.setattr('utils.request_handling.get_blog_id', mock_get_blog_id)

        with pytest.raises(RuntimeError):
            assert await req.input_blog_address(session)


@pytest.mark.asyncio
async def test_input_blog_address_output_name_validation(monkeypatch, capsys):
    """
    Test for checking if proper messages are presented to the user while inputting invalid values.
    It simulates inputting unaccepted blob's name.
    Ends with raising StopIteration.
    :param monkeypatch: Pytest's built-in fixture
    :param capsys: Pytest's built-in fixture
    :return: None
    """
    valid = 'learningpythonway'
    invalid = 'http://foobar.blogspot.com'
    user_inputs = iter([invalid, invalid, invalid])
    valid_url = f'https://{valid}.blogspot.com/'
    id = '12345'

    def mock_input_func():
        return next(user_inputs)

    async def mock_validate_blog_name(name):
        return name == valid

    async def mock_check_response_code(name, session):
        return True

    async def mock_is_blogger(url, session):
        return True

    async def mock_get_blog_id(url, session):
        return id

    async with aiohttp.ClientSession() as session:
        monkeypatch.setattr('utils.request_handling.input_func', mock_input_func)
        monkeypatch.setattr('utils.request_handling.validate_blog_name', mock_validate_blog_name)
        monkeypatch.setattr('utils.request_handling.check_response_code', mock_check_response_code)
        monkeypatch.setattr('utils.request_handling.is_blogger', mock_is_blogger)
        monkeypatch.setattr('utils.request_handling.get_blog_id', mock_get_blog_id)

        # with pytest.raises(RuntimeError):
        assert await req.input_blog_address(session)
        captured = capsys.readouterr()
        assert 'Inputted value contains more than blog`s name.' in captured.out
        assert 'Requested blog seems to not respond, try one more time.' not in captured.out


@pytest.mark.asyncio
async def test_input_blog_address_output_response_validation(monkeypatch, capsys):
    """
    Test designed to check for validity of messages presented to the user, when response code
    is else than 200.
    :param monkeypatch: Pytest's built-in fixture
    :param capsys: Pytest's built-in fixture
    :return: None
    """
    valid = 'learningpythonway'
    invalid = 'http://foobarbazbazsuperduper.blogspot.com'
    user_inputs = iter([invalid, invalid, invalid])
    valid_url = f'https://{valid}.blogspot.com/'
    id = '12345'

    def mock_input_func():
        return next(user_inputs)

    async def mock_validate_blog_name(name):
        return True

    async def mock_check_response_code(name, session):
        return name == valid

    async def mock_is_blogger(url, session):
        return True

    async def mock_get_blog_id(url, session):
        return id

    async with aiohttp.ClientSession() as session:
        monkeypatch.setattr('utils.request_handling.input_func', mock_input_func)
        monkeypatch.setattr('utils.request_handling.validate_blog_name', mock_validate_blog_name)
        monkeypatch.setattr('utils.request_handling.check_response_code', mock_check_response_code)
        monkeypatch.setattr('utils.request_handling.is_blogger', mock_is_blogger)
        monkeypatch.setattr('utils.request_handling.get_blog_id', mock_get_blog_id)

        assert await req.input_blog_address(session)
        captured = capsys.readouterr()
        assert 'Inputted value contains more than blog`s name.' not in captured.out
        assert 'Requested blog seems to not respond, try one more time.' in captured.out


@pytest.mark.asyncio
async def test_validate_blog_name():
    names = iter(['https://blog', 'blog.blogspot.com',
                  'http://bloggg', 'blog.com/',
                  'blog/', 'blog'])

    def provide_names():
        return next(names)

    assert await req.validate_blog_name(provide_names()) is False, 'Should be False but is True'
    assert await req.validate_blog_name(provide_names()) is False, 'Should be False but is True'
    assert await req.validate_blog_name(provide_names()) is False, 'Should be False but is True'
    assert await req.validate_blog_name(provide_names()) is False, 'Should be False but is True'
    assert await req.validate_blog_name(provide_names()) is False, 'Should be False but is True'
    assert await req.validate_blog_name(provide_names()) is True, 'Should be True but is False'


# TODO Change the way of testing, to one using pytest async_aiohttp. Use tutorial on package docs
#  by setting a web app, and serwer responses responses.
def test_response_code(requests_mock):
    """
    Test for intercepting requests and mocking the responses.
    Asserts function behaviour for different response codes.
    :param requests_mock: requests_mock fixture, for intercepting requests send to HTTP servers.
    :return: None
    """
    valid_response = 'foobazbar'
    invalid_response = 'foobazbaromg'
    totally_wrong_url = 'some_verry_bad_url.blogspot.pl'
    blogs = iter([valid_response, invalid_response, totally_wrong_url])

    def provide_data():
        name_ = next(blogs)
        address = f'https://{name_}.blogspot.com/'
        return name_, address

    name, url = provide_data()
    requests_mock.get(url, status_code=200)
    assert req.check_response_code(name) is True
    name, url = provide_data()
    requests_mock.get(url, status_code=404)
    assert req.check_response_code(name) is False
    name, url = provide_data()
    requests_mock.get(url, exc=requests.ConnectionError)
    assert req.check_response_code(name) is False


# def test_is_blogger(requests_mock):
#     """
#     Test for intercepting requests and mocking the responses.
#     Asserts function behaviour for different response text. Validates if url is a .blogger.com blog
#     :param requests_mock: requests_mock fixture, for intercepting requests send to HTTP servers.
#     :return: None
#     """
#     url = 'https://validresponse.blogspot.com/'
#     res_text = '''some fancy text containing some fancy link as .blogger.com/
#      and even more fancy text containing <meta content='blogger' name='generator'/>
#      and some more links containing /feeds/posts/default and some more text'''
#     requests_mock.get(url, text=res_text)
#     assert req.is_blogger(url) is True
#
#     url = 'https://invalidresponse.blogspot.com/'
#     res_text = '''some fancy text missing some fancy link as b _ l _ o_gger._com/
#      and even more fancy text containing <meta content='blogger' name='generator'/>
#      and some more links containing /feeds/posts/default and some more text'''
#     requests_mock.get(url, text=res_text)
#     assert req.is_blogger(url) is None
#
#     url = 'https://invalidresponse.blogspot.com/'
#     res_text = '''some fancy text containing some fancy link as .blogger.com/
#      and even more fancy text containing <meta content='blogger' but wait now way this is here!
#      name='generator'/>
#      and some more links containing /feeds/posts/default and some more text'''
#     requests_mock.get(url, text=res_text)
#     assert req.is_blogger(url) is None
#
#     url = 'https://invalidresponse.blogspot.com/'
#     res_text = '''some fancy text containing some fancy link as .blogger.com/
#      and even more fancy text containing <meta content='blogger' name='generator'/>
#      and some more links containing /feedsaresonothere/postsarelost/defaultdefalttoNone
#      and some more text'''
#     requests_mock.get(url, text=res_text)
#     assert req.is_blogger(url) is None
#
#
# def test_get_blog_id(requests_mock):
#     """
#     Test for intercepting requests and mocking the responses.
#     Asserts function behaviour for different response text. Validates if function extracts blog ID
#     :param requests_mock: requests_mock fixture, for intercepting requests send to HTTP servers.
#     :return: None
#     """
#     url = 'https://validresponse.blogspot.com/'
#     mocked_url = 'https://validresponse.blogspot.com/feeds/posts/default'
#     res_text = '''fancy text containing >blog-66666666699996< and nothing more i think :)'''
#     requests_mock.get(mocked_url, text=res_text)
#     assert req.get_blog_id(url) == '66666666699996'
#
#     url = 'https://validresponse.blogspot.com/'
#     mocked_url = 'https://validresponse.blogspot.com/feeds/posts/default'
#     res_text = '''fancy text containing >blog-1234567890< and nothing more i think :)'''
#     requests_mock.get(mocked_url, text=res_text)
#     assert req.get_blog_id(url) == '1234567890'
#
#     url = 'https://invalidresponse.blogspot.com/'
#     mocked_url = 'https://invalidresponse.blogspot.com/feeds/posts/default'
#     res_text = '''fancy text containing >1234567890< and nothing more i think :)'''
#     requests_mock.get(mocked_url, text=res_text)
#     assert req.get_blog_id(url) is None
#
#     url = 'https://invalidresponse.blogspot.com/'
#     mocked_url = 'https://invalidresponse.blogspot.com/feeds/posts/default'
#     res_text = '''fancy text containing >blog-< and nothing more i think :)'''
#     requests_mock.get(mocked_url, text=res_text)
#     assert req.get_blog_id(url) is None
#     #
#     url = 'https://invalidresponse.blogspot.com/'
#     mocked_url = 'https://invalidresponse.blogspot.com/feeds/posts/default'
#     res_text = '''but wait! where is the blog id?'''
#     requests_mock.get(mocked_url, text=res_text)
#     assert req.get_blog_id(url) is None
