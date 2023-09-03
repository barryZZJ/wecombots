import time
import httpx
from bs4 import BeautifulSoup
from sympy import Eq, solveset
from sympy.abc import x
from checker import BaseChecker

# 0 10 * * * ~/doki8checkin/checkin.sh

# SERVERCHAN_KEY = 'SCT164400THDN7R51ck5uOz8H3MAhIejfR'

# def push(key, title, content=None):
#     url = 'https://sctapi.ftqq.com/{}.send'.format(key)
#     params = {
#         'title': title
#     }
#     if content:
#         params['content'] = content
#     c.get(url, params=params)


class AuthError(BaseException):
    ...

class URL:
    login = '/login'

c = httpx.Client(
    base_url='http://www.doki8.net',
    headers={
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0",
    }
)


template = {
    'log': 'bazinga123',
    'pwd': 'zzjzzj0123',
    'mc-value': '',
    'wp-submit': '登录',
    'redirect_to': 'http://www.doki8.com/members/bazinga123/pointhistory/?loggedout=true',
    'testcookie': '1',
}

OPERATOR_TABLE = str.maketrans('+−×', '+-*')

def fuck_captcha() -> str:
    resp = c.get(URL.login)
    parsed = BeautifulSoup(resp.text, 'html.parser')
    span = parsed.select_one('.math-captcha-form>span')
    # span.contents example:
    # ['9 + 1 = ', <input aria-required="true" class="mc-input" id="mc-input" length="2" name="mc-value" size="2" type="text" value=""/>]
    # ['83 + ', <input aria-required="true" class="mc-input" id="mc-input" length="2" name="mc-value" size="2" type="text" value=""/>, ' = 88']
    # [<input aria-required="true" class="mc-input" id="mc-input" length="2" name="mc-value" size="2" type="text" value=""/>, ' − 4 = 4']
    print(span)
    equationstr = ''.join(str(expr) if isinstance(expr, str) else 'x' for expr in span.contents)
    equationstr = equationstr.translate(OPERATOR_TABLE)
    # '9 + 1 = x' or '83 + x = 88' or 'x - 4 = 4'
    lhs, rhs = map(eval, equationstr.split('='))
    equation = Eq(lhs, rhs)
    solution = solveset(equation, x)
    print(str(solution.args[0]))
    return str(solution.args[0])

def login():
    RETRY = 2
    TIMEOUT = 2
    data = template.copy()
    # get WordPress cookie, otherwise can't do post.
    c.get(URL.login)
    data['mc-value'] = fuck_captcha()
    # print(data['captcha'])
    for _ in range(RETRY):
        resp = c.post(URL.login, data=data)
        # print(resp.text)
        if resp.has_redirect_location or resp.status_code == 302:
            return True
        parsed = BeautifulSoup(resp.text, 'html.parser')
        if res := parsed.find(id='login_error'):
            if 'captcha' in res.text.strip().lower():
                print('wrong captcha, retrying...')
                time.sleep(TIMEOUT)
                data['captcha'] = fuck_captcha()
                continue
            raise AuthError(res.decode_contents().strip())
        raise AuthError('Unexpected error: ' + str(res))
    raise AuthError('wrong captcha for ' + str(RETRY) + ' times!')


class Doki8Checker(BaseChecker):
    def __init__(self, retry: int = 3, timeout: int = 60):
        super().__init__('心动日剧', retry, timeout)

    def _check(self, *args, **kwargs):
        login()

