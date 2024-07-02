import pytest
import json
import sys
import requests_mock
import requests
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
    assert req.validate_error_message(request, requests) is True, 'should be True but was False'
    request = 'by_url'
    assert req.validate_error_message(request, requests) is True, 'should be True but was False'
    request = 'posts'
    assert req.validate_error_message(request, requests) is True, 'should be True but was False'
    request = 'search'
    assert req.validate_error_message(request, requests) is True, 'should be True but was False'
    request = 'by_path'
    assert req.validate_error_message(request, requests) is True, 'should be True but was False'
    request = 'comments'
    assert req.validate_error_message(request, requests) is True, 'should be True but was False'


def test_validate_error_message_key_absent():
    requests = test_requests.copy()
    request = 'by_by'
    assert req.validate_error_message(request, requests) is False, 'should be False but was True'
    request = 'foo'
    assert req.validate_error_message(request, requests) is False, 'should be False but was True'
    request = 'bar'
    assert req.validate_error_message(request, requests) is False, 'should be False but was True'
    request = 'i hate python`s path management'
    assert req.validate_error_message(request, requests) is False, 'should be False but was True'


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


def test_input_blog_address_goes_towards_validation(monkeypatch):
    """
    Test for simulating user inputs ending with positive input and assertion
    :param monkeypatch: Pytest's built-in fixture
    :return: None
    """
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
    """
    Test for simulating user inputs, ending with no valid input and exception raising
    :param monkeypatch: Pytest's built-in fixture
    :return: None
    """
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


def test_input_blog_address_output_name_validation(monkeypatch, capsys):
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

    def mock_input_func():
        return next(user_inputs)

    def mock_validate_blog_name(name):
        return name == valid

    def mock_check_response_code():
        return True

    monkeypatch.setattr('utils.request_handling.input_func', mock_input_func)
    monkeypatch.setattr('utils.request_handling.validate_blog_name', mock_validate_blog_name)
    monkeypatch.setattr('utils.request_handling.check_response_code', mock_check_response_code)

    with pytest.raises(StopIteration):
        assert req.input_blog_address()
    captured = capsys.readouterr()
    assert 'Inputted value contains more than blog`s name.' in captured.out
    assert 'Requested blog seems to not respond, try one more time.' not in captured.out


def test_input_blog_address_output_response_validation(monkeypatch, capsys):
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

    def mock_input_func():
        return next(user_inputs)

    def mock_validate_blog_name(name):
        return True

    def mock_check_response_code(name):
        return name == valid

    monkeypatch.setattr('utils.request_handling.input_func', mock_input_func)
    monkeypatch.setattr('utils.request_handling.validate_blog_name', mock_validate_blog_name)
    monkeypatch.setattr('utils.request_handling.check_response_code', mock_check_response_code)

    with pytest.raises(StopIteration):
        assert req.input_blog_address()
    captured = capsys.readouterr()
    assert 'Inputted value contains more than blog`s name.' not in captured.out
    assert 'Requested blog seems to not respond, try one more time.' in captured.out


def test_validate_blog_name():
    names = iter(['https://blog', 'blog.blogspot.com',
                  'http://bloggg', 'blog.com/',
                  'blog/', 'blog'])

    def provide_names():
        return next(names)

    assert req.validate_blog_name(provide_names()) is False, 'Should be False but is True'
    assert req.validate_blog_name(provide_names()) is False, 'Should be False but is True'
    assert req.validate_blog_name(provide_names()) is False, 'Should be False but is True'
    assert req.validate_blog_name(provide_names()) is False, 'Should be False but is True'
    assert req.validate_blog_name(provide_names()) is False, 'Should be False but is True'
    assert req.validate_blog_name(provide_names()) is True, 'Should be True but is False'


def test_response_code(requests_mock):
    valid_response = 'foobazbar'
    invalid_response = 'foobazbaromg'
    totally_wrong_url = 'some_verry_bad_url.blogspot.pl'
    blogs = iter([valid_response, invalid_response, totally_wrong_url])

    def provide_data():
        name_ = next(blogs)
        address = f'https://{name_}.blogspot.com/'
        return name_, address

    # # Uncomment this to test real responses
    # assert req.check_response_code(provide_data()) is True
    # assert req.check_response_code(provide_data()) is False
    # assert req.check_response_code(provide_data()) is False

    # mock responses comment out if user wants to conduct test with real responses.
    name, url = provide_data()
    requests_mock.get(url, status_code=200)
    assert req.check_response_code(name) is True
    name, url = provide_data()
    requests_mock.get(url, status_code=404)
    assert req.check_response_code(name) is False
    name, url = provide_data()
    requests_mock.get(url, exc=requests.ConnectionError)
    assert req.check_response_code(name) is False

# TODO tests for is_blogger and get_blog_id remains.
#  Both to do with mock response.text.
