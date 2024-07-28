import re
import json
import aiohttp
import asyncio
import config.config as cnf


class ConnectionPool:
    __session = None

    @classmethod
    async def get_session(cls) -> aiohttp.ClientSession:
        if cls.__session is None:
            cls.__session = aiohttp.ClientSession()
        return cls.__session


def input_func() -> str:
    the_input = input('Type in blog`s name: ')
    if len(the_input) == 0:
        the_input = cnf.BASE_BLOG_NAME
    return the_input


async def input_blog_address(s: aiohttp.ClientSession) -> str:
    print('What blog hosted on Blogger would you like to see? Omit .blogspot.com and http parts.')
    blog_name = input_func()
    ok_name = False
    ok_conn = False
    ok_blogger = False
    blog_id = False
    while not ok_name and not ok_conn and not ok_blogger and not blog_id:
        blog_url = f'https://{blog_name}.blogspot.com/'
        async with asyncio.TaskGroup() as tg:
            ok_name = tg.create_task(validate_blog_name(blog_name))
            ok_conn = tg.create_task(check_response_code(blog_url, s))
            ok_blogger = tg.create_task(is_blogger(blog_url, s))
            blog_id = tg.create_task(get_blog_id(blog_url, s))
            ok_name, ok_conn, ok_blogger, blog_id = await asyncio.gather(
                ok_name, ok_conn, ok_blogger, blog_id)
        if not ok_name:
            print('Inputted value contains more than blog`s name.')
            blog_name = input_func()
            continue
        if not ok_conn:
            print('Requested blog seems to not respond, try one more time.')
            blog_name = input_func()
            continue
        if not ok_blogger:
            print('Requested blog seems not to be on blogger platform, try one more time.')
            blog_name = input_func()
            continue
        if not blog_id:
            print('Requested blog seems not to have an ID, try one more time.')
            blog_name = input_func()
            continue
    return blog_id


async def validate_blog_name(name: str) -> bool:
    user_input = name.lower().strip()
    hits = re.compile(r'^https?|/$|\Dblogspot|\Dcom|[\s!@#$%&*+=,[]{}\\/:;?.]| ')
    if not bool(re.search(hits, user_input)):
        print('Name Valid')
        return True
    else:
        print('Name Invalid')
        return False


async def check_response_code(to_check: str, session: aiohttp.ClientSession) -> bool:
    url = to_check
    try:
        async with session.get(url) as r:
            if r.status == 200:
                print('Connection Valid')
                return True
            else:
                print('Connection Invalid')
                return False
    except (aiohttp.client_exceptions.InvalidURL,
            aiohttp.client_exceptions.ClientConnectorError,
            aiohttp.client_exceptions.ClientConnectionError):
        print('Connection Error')
        return False


async def is_blogger(url: str, session: aiohttp.ClientSession) -> bool:
    link = re.compile(r'.blogger.com/')
    generator = re.compile(r"<meta content='blogger' name='generator'/>")
    feed = re.compile(r'/feeds/posts/default')
    blogger_in_link = False
    blogger_as_generator = False
    feed_in_link = False
    try:
        async with session.get(url) as r:
            # r.encoding = 'utf-8'
            async for chunk in r.content.iter_chunked(1024):
                decoded = chunk.decode('utf-8')
                if not blogger_in_link:
                    blogger_in_link = bool(re.search(link, decoded))
                if not blogger_as_generator:
                    blogger_as_generator = bool(re.search(generator, decoded))
                if not feed_in_link:
                    feed_in_link = bool(re.search(feed, decoded))
                if all([blogger_in_link, blogger_as_generator, feed_in_link]):
                    print('Blogger Valid')
                    return True
            print('Blogger Invalid')
            return False
    except (aiohttp.client_exceptions.InvalidURL,
            aiohttp.client_exceptions.ClientConnectorError,
            aiohttp.client_exceptions.ClientConnectionError):
        print('Blogger Connection Error')
        return False


async def get_blog_id(url: str, session: aiohttp.ClientSession) -> str | bool:
    blog_pattern = re.compile(r'blog-([0-9]+)<', re.I)
    # user_pattern = re.compile(r'profile/([0-9]*)<', re.I)
    blog_id = ''
    url = f'{url}feeds/posts/default'
    try:
        async with session.get(url) as r:
            # r.encoding = 'utf-8'
            async for chunk in r.content.iter_chunked(1600):
                decoded = chunk.decode('utf-8')
                # print(chunk)
                if not blog_id:
                    blog_id = re.search(blog_pattern, decoded)
                if blog_id is not None:
                    return blog_id.group(1)  # .decode(encoding='utf-8')
            return False
    except (aiohttp.client_exceptions.InvalidURL,
            aiohttp.client_exceptions.ClientConnectorError,
            aiohttp.client_exceptions.ClientConnectionError):
        return False


def return_request_url(req_type: str, blog_url: str = None, blog_id: str = None,
                       post_id: str = None, auth: str = None, phrase: str = None,
                       post_path: str = None, base_req_body: str = cnf.API_BASE_REQ) -> str:
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
        raise ValueError(f'Variable req_type "{req_type}" not included in possible requests: '
                         f'{req_type not in req_types}, \nor variables needed for request creation '
                         f'are missing: {none_val_in_req}')
    else:
        return req_types.get(req_type)


def validate_error_message(request: str, requests_pool: dict) -> bool:
    if request not in requests_pool.keys():
        return False
    else:
        try:
            none_present = 'None' in requests_pool.get(request)
        except TypeError:
            return False
    return none_present


async def extract_blog_info(key: str, blog_id: str, session: aiohttp.ClientSession) -> json:
    req_url = return_request_url(req_type='by_id', blog_id=blog_id, auth=key)
    async with session.get(req_url) as r:
        dump = await r.json(encoding='utf-8')
        return dump


async def get_posts(url, session, next_page=None):
    url += f'&pageToken={next_page}' if next_page else ''
    async with session.get(url) as resp:
        dump = await resp.json(encoding='utf-8')
        print('token in get_posts', dump.get('nextPageToken', None))
        return dump.get('items', []), dump.get('nextPageToken', None)


async def extract_posts_info(key: str, blog_id: str, session: aiohttp.ClientSession) -> json:
    req_url = return_request_url(req_type='posts', blog_id=blog_id, auth=key)
    posts = []
    next_page = None
    # batch_size = 5
    counter = 0
    titles = []
    the_first_post = False

    while True:
        tasks = [get_posts(req_url, session, next_page)]
        results = await asyncio.gather(*tasks)
        for items, next_page in results:
            posts.extend(items)
            print(f'next_page is {next_page}')
            for post in items:
                if post.get('title', '') not in titles:
                    titles.append(post.get('title', ''))
                if 'Jabłuszkowiec - ciasto ucierane z jabłkami' in post.get('title', ''):
                    the_first_post = True
        if not next_page:
            counter += 1
            if counter >= 2:
                print(counter)
                print('In break')
                break

    # tasks = []
        # for _ in range(batch_size):
        #     tasks.append(get_posts(req_url, session, next_page))
        #     # next_page = None
        # results = await asyncio.gather(*tasks)
        # for items, next_page in results:
        #     posts.extend(items)
        #     print(f'next_page is {next_page}')
        #     for post in items:
        #         if post.get('title', '') not in titles:
        #             titles.append(post.get('title', ''))
        #         if 'Jabłuszkowiec - ciasto ucierane z jabłkami' in post.get('title', ''):
        #             the_first_post = True
        # if not next_page:
        #     counter += 1
        #     if counter >= 20:
        #         print(counter)
        #         print('In break')
        #         break

    print('Found first post:', the_first_post)
    print(titles)
    print(len(titles))
    print(len(posts))
    return posts


async def get_more_posts(url, token, session):
    url += f'&pageToken={token}'
    async with session.get(url) as r:
        data = await r.json(encoding='utf-8')
        next_page = data.get('nextPageToken', '')
        next_batch = data.get('items', [])
    return next_page, next_batch

