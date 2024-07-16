import pytest
import json
import sys
import aiohttp
# import asyncio
from aioresponses import aioresponses
from aiohttp import ClientSession

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


@pytest.mark.asyncio
async def test_connection_pool():
    async with await req.ConnectionPool.get_session() as session:
        async with await req.ConnectionPool.get_session() as second:
            assert session is second


def test_validate_error_message_key_present() -> None:
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


def test_validate_error_message_key_absent() -> None:
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


def test_validate_error_message_typeerr() -> None:
    request_type = {
        'by_url': 'https://www.googleapis.com/blogger/v3/blogs/byurl?url=?key=',
        'by_id': 44}

    request = 'by_id'
    assert (
            req.validate_error_message(request, request_type) is False
    ), 'should be False but was True'


def test_req_types_return() -> None:
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


def test_req_types_return_exception_raising() -> None:
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


def test_check_input_func(monkeypatch: pytest.MonkeyPatch) -> None:
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
    monkeypatch.setattr('builtins.input', lambda _: '')
    assert req.input_func() == cnf.BASE_BLOG_NAME


def test_raise_error_input_func(monkeypatch: pytest.MonkeyPatch) -> None:
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
async def test_input_blog_address_goes_towards_validation(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test for simulating user inputs ending with positive input and assertion
    :param monkeypatch: Pytest's built-in fixture
    :return: None
    """
    valid = 'learningpythonway'
    invalid = 'http://foobar.blogspot.com'
    valid_url = f'https://{valid}.blogspot.com/'
    invalid_url = f'https://{invalid}.blogspot.com/'
    id = '12345'
    user_inputs = iter([invalid, invalid, invalid, valid])

    def mock_input_func() -> str:
        return next(user_inputs)

    async def mock_validate_blog_name(name: str) -> bool:
        return name == valid

    async def mock_check_response_code(url: str, session: ClientSession()) -> bool:
        return url == valid_url

    async def mock_is_blogger(url: str, session: ClientSession()) -> bool:
        return url == valid_url

    async def mock_get_blog_id(url: str, session: ClientSession()) -> str | bool:
        if url == valid_url:
            return id
        return False

    async with ClientSession() as session:
        monkeypatch.setattr('utils.request_handling.input_func', mock_input_func)
        monkeypatch.setattr('utils.request_handling.validate_blog_name', mock_validate_blog_name)
        monkeypatch.setattr('utils.request_handling.check_response_code', mock_check_response_code)
        monkeypatch.setattr('utils.request_handling.is_blogger', mock_is_blogger)
        monkeypatch.setattr('utils.request_handling.get_blog_id', mock_get_blog_id)

        assert await req.input_blog_address(session) == '12345'


@pytest.mark.asyncio
async def test_input_blog_address_raises_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
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

    def mock_input_func() -> str:
        return next(user_inputs)

    async def mock_validate_blog_name(name: str) -> bool:
        return name == valid

    async def mock_check_response_code(name: str, session: ClientSession()) -> bool:
        return name == valid

    async def mock_is_blogger(url: str, session: ClientSession()) -> bool:
        return url == valid_url

    async def mock_get_blog_id(url: str, session: ClientSession()) -> str | bool:
        return False

    async with ClientSession() as session:
        monkeypatch.setattr('utils.request_handling.input_func', mock_input_func)
        monkeypatch.setattr('utils.request_handling.validate_blog_name', mock_validate_blog_name)
        monkeypatch.setattr('utils.request_handling.check_response_code', mock_check_response_code)
        monkeypatch.setattr('utils.request_handling.is_blogger', mock_is_blogger)
        monkeypatch.setattr('utils.request_handling.get_blog_id', mock_get_blog_id)

        with pytest.raises(RuntimeError):
            assert await req.input_blog_address(session)


@pytest.mark.asyncio
async def test_input_blog_address_output_name_validation(monkeypatch: pytest.MonkeyPatch,
                                                         capsys: pytest.fixture) -> None:
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

    def mock_input_func() -> str:
        return next(user_inputs)

    async def mock_validate_blog_name(name: str) -> bool:
        return name == valid

    async def mock_check_response_code(name: str, session: ClientSession) -> bool:
        return True

    async def mock_is_blogger(url: str, session: ClientSession) -> bool:
        return True

    async def mock_get_blog_id(url: str, session: ClientSession) -> str | bool:
        return id

    async with ClientSession() as session:
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
async def test_input_blog_address_output_response_validation(monkeypatch: pytest.MonkeyPatch,
                                                             capsys: pytest.fixture) -> None:
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

    def mock_input_func() -> str:
        return next(user_inputs)

    async def mock_validate_blog_name(name:str) -> bool:
        return True

    async def mock_check_response_code(name: str, session: ClientSession) -> bool:
        return name == valid

    async def mock_is_blogger(url: str, session: ClientSession) -> bool:
        return True

    async def mock_get_blog_id(url: str, session: ClientSession) -> str | bool:
        return id

    async with ClientSession() as session:
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
async def test_input_blog_address_output_is_blogger(monkeypatch: pytest.MonkeyPatch,
                                                             capsys: pytest.fixture) -> None:
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

    def mock_input_func() -> str:
        return next(user_inputs)

    async def mock_validate_blog_name(name:str) -> bool:
        return True

    async def mock_check_response_code(name: str, session: ClientSession) -> bool:
        return True

    async def mock_is_blogger(url: str, session: ClientSession) -> bool:
        return False

    async def mock_get_blog_id(url: str, session: ClientSession) -> str | bool:
        return id

    async with ClientSession() as session:
        monkeypatch.setattr('utils.request_handling.input_func', mock_input_func)
        monkeypatch.setattr('utils.request_handling.validate_blog_name', mock_validate_blog_name)
        monkeypatch.setattr('utils.request_handling.check_response_code', mock_check_response_code)
        monkeypatch.setattr('utils.request_handling.is_blogger', mock_is_blogger)
        monkeypatch.setattr('utils.request_handling.get_blog_id', mock_get_blog_id)

        assert await req.input_blog_address(session)
        captured = capsys.readouterr()
        assert 'Requested blog seems not to have an ID, try one more time.' not in captured.out
        assert ('Requested blog seems not to be on blogger platform, try one more time.'
                in captured.out)


@pytest.mark.asyncio
async def test_input_blog_address_output_get_blog_id(monkeypatch: pytest.MonkeyPatch,
                                                             capsys: pytest.fixture) -> None:
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
    valid_url = f'https://{invalid}.blogspot.com/'
    id = '12345'

    def mock_input_func() -> str:
        return next(user_inputs)

    async def mock_validate_blog_name(name:str) -> bool:
        return True

    async def mock_check_response_code(name: str, session: ClientSession) -> bool:
        return True

    async def mock_is_blogger(url: str, session: ClientSession) -> bool:
        return True

    async def mock_get_blog_id(url: str, session: ClientSession) -> str | bool:
        return False

    async with ClientSession() as session:
        monkeypatch.setattr('utils.request_handling.input_func', mock_input_func)
        monkeypatch.setattr('utils.request_handling.validate_blog_name', mock_validate_blog_name)
        monkeypatch.setattr('utils.request_handling.check_response_code', mock_check_response_code)
        monkeypatch.setattr('utils.request_handling.is_blogger', mock_is_blogger)
        monkeypatch.setattr('utils.request_handling.get_blog_id', mock_get_blog_id)

        with pytest.raises(AssertionError):
            assert await req.input_blog_address(session)
        captured = capsys.readouterr()
        # assert 'Requested blog seems to not respond, try one more time.' not in captured.out
        assert 'Requested blog seems not to have an ID, try one more time.' in captured.out


@pytest.mark.asyncio
async def test_validate_blog_name() -> None:
    names = iter(['https://blog', 'blog.blogspot.com',
                  'http://bloggg', 'blog.com/',
                  'blog/', 'blog'])

    def provide_names() -> str:
        return next(names)

    assert await req.validate_blog_name(provide_names()) is False, 'Should be False but is True'
    assert await req.validate_blog_name(provide_names()) is False, 'Should be False but is True'
    assert await req.validate_blog_name(provide_names()) is False, 'Should be False but is True'
    assert await req.validate_blog_name(provide_names()) is False, 'Should be False but is True'
    assert await req.validate_blog_name(provide_names()) is False, 'Should be False but is True'
    assert await req.validate_blog_name(provide_names()) is True, 'Should be True but is False'


@pytest.mark.asyncio
async def test_response_code_aiosesponses(capsys: pytest.fixture) -> None:
    """
    Test for intercepting requests and mocking the responses.
    Asserts function behaviour for different response codes.
    :param capsys: Pytest's built-in fixture
    :return: None
    """
    valid = 'https://validresponse.blogspot.com/'
    invalid = 'https://invalidvalidresponse.blogspot.com/'
    error = 'https://errorresponse.blogspot.com/'

    async with ClientSession() as s:
        with aioresponses() as r:
            r.get(valid, status=200)
            resp = await req.check_response_code(valid, s)
            assert resp is True
        with aioresponses() as rr:
            rr.get(invalid, status=400)
            resp = await req.check_response_code(invalid, s)
            assert resp is False
        with aioresponses() as err:
            err.get(error, exception=aiohttp.client_exceptions.InvalidURL(error))
            resp = await req.check_response_code(error, s)
            assert resp is False

    collected = capsys.readouterr()
    assert 'Connection Valid' in collected.out
    assert 'Connection Invalid' in collected.out
    assert 'Connection Error' in collected.out


@pytest.mark.asyncio
async def test_is_blogger(capsys: pytest.fixture) -> None:
    """
    Test for intercepting requests and mocking the responses.
    Asserts response body for different situations
    :param capsys: Pytest's built-in fixture
    :return: None
    """

    url_val = 'http://validresponse.blogspot.com/'
    url_inval_1 = 'https://invalidresponse1.blogspot.com/'
    url_inval_2 = 'https://invalidresponse2.blogspot.com/'
    url_inval_3 = 'https://invalidresponse3.blogspot.com/'
    url_error = 'https://errorresponse.blogspot.com/'
    res_val = '''some fancy text containing some fancy link as .blogger.com/
     and even more fancy text containing <meta content='blogger' name='generator'/>
     and some more links containing /feeds/posts/default and some more text'''
    res_inval_1 = '''some fancy text missing some fancy link as b _ l _ o_gger._com/
     and even more fancy text containing <meta content='blogger' name='generator'/>
     and some more links containing /feeds/posts/default and some more text'''
    res_inval_2 = '''some fancy text containing some fancy link as .blogger.com/
     and even more fancy text containing <meta content='blogger' but wait now way this is here!
     name='generator'/>
     and some more links containing /feeds/posts/default and some more text'''
    res_inval_3 = '''some fancy text containing some fancy link as .blogger.com/
     and even more fancy text containing <meta content='blogger' name='generator'/>
     and some more links containing /feedsaresonothere/postsarelost/defaultdefalttoNone
     and some more text'''

    async with ClientSession() as s:
        with aioresponses() as r:
            r.get(url_val, body=res_val)
            resp = await req.is_blogger(url_val, s)
            assert resp is True
            r.get(url_inval_1, body=res_inval_1)
            resp = await req.is_blogger(url_inval_1, s)
            assert resp is False
            r.get(url_inval_2, body=res_inval_2)
            resp = await req.is_blogger(url_inval_2, s)
            assert resp is False
            r.get(url_inval_3, body=res_inval_3)
            resp = await req.is_blogger(url_inval_3, s)
            assert resp is False
            r.get(url_error, exception=aiohttp.client_exceptions.ClientConnectionError())
            resp = await req.is_blogger(url_error, s)
            assert resp is False
            captured = capsys.readouterr()
            assert 'Blogger Valid' in captured.out
            assert 'Blogger Invalid' in captured.out
            assert 'Blogger Connection Error' in captured.out


@pytest.mark.asyncio
async def test_get_blog_id(capsys: pytest.fixture) -> None:
    """
    Test for intercepting requests and mocking the responses.
    Asserts response body for blog id number.
    :param capsys: Pytest's built-in fixture
    :return: None
    """

    valid = 'https://validresponse.blogspot.com/'
    mocked_valid = 'https://validresponse.blogspot.com/feeds/posts/default'
    invalid = 'https://invalidresponse.blogspot.com/'
    mocked_invalid = 'https://invalidresponse.blogspot.com/feeds/posts/default'
    error = 'https://errorrsponse.blogspot.com/'
    mocked_error = 'https://errorrsponse.blogspot.com/feeds/posts/default'

    async with ClientSession() as s:
        with aioresponses() as r:
            r.get(mocked_valid,
                  body='fancy text containing >blog-66666666699996< and nothing more I think :)')
            resp = await req.get_blog_id(valid, s)
            assert resp == '66666666699996'
            r.get(mocked_valid,
                  body='fancy text containing >blog-1234567890< and nothing more I think :)')
            resp = await req.get_blog_id(valid, s)
            assert resp == '1234567890'
            r.get(mocked_invalid,
                  body='fancy text containing >1234567890< and nothing more I think :)')
            resp = await req.get_blog_id(invalid, s)
            assert resp is False
            r.get(mocked_invalid, body='fancy text containing >blog-< and nothing more i think :)')
            resp = await req.get_blog_id(invalid, s)
            assert resp is False
            r.get(mocked_invalid, body='but wait! where is the blog id?')
            resp = await req.get_blog_id(invalid, s)
            assert resp is False
            r.get(mocked_error, body='oh no! and error! what do we do?!',
                  exception=aiohttp.client_exceptions.InvalidURL(mocked_error))
            resp = await req.get_blog_id(error, s)
            assert resp is False

