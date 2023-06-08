import time
import httpx
import ddddocr
from bs4 import BeautifulSoup

import wecomsan
from config import load_conf

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


def report(title, content=None):
    print('title:', title, '\ncontent:', content)
    msg = f'{title}\n{content}'
    conf = load_conf()
    bot = wecomsan.WecomSan(**conf['bot'])
    bot.send(msg)
    # push(SERVERCHAN_KEY, title, content)

class AuthError(BaseException):
    ...

class URL:
    login = '/wp-login.php'
    captcha = '/wp-content/plugins/dx-login-register/extends/captcha/captcha.php'

c = httpx.Client(
    base_url='http://www.doki8.net',
    headers={
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0",
    }
)

ocr = ddddocr.DdddOcr()

template = {
    'log': 'bazinga123',
    'pwd': 'zzjzzj0123',
    'captcha': '',
    'wp-submit': '登录',
    'redirect_to': 'http://www.doki8.com/members/bazinga123/pointhistory/?loggedout=true',
    'testcookie': '1',
}

def fuck_captcha() -> str:
    resp = c.get(URL.captcha)
    captcha = ocr.classification(resp.content)
    # with open('tmp.png', 'wb') as f:
    #     f.write(resp.content)
    return captcha

def login():
    RETRY = 5
    TIMEOUT = 2
    c.get(URL.login)
    data = template.copy()
    data['captcha'] = fuck_captcha()
    # print(data['captcha'])
    for _ in range(RETRY):
        resp = c.post(URL.login, data=data)
        # print(resp.text)
        if resp.has_redirect_location or resp.status_code == 302:
            return True
        parsed = BeautifulSoup(resp.text, 'html.parser')
        if res:=parsed.find(id='login_error'):
            if '验证码' in res.text.strip():
                print('wrong captcha, retrying...')
                time.sleep(TIMEOUT)
                data['captcha'] = fuck_captcha()
                continue
            raise AuthError(res.decode_contents().strip())
        raise AuthError('Unexpected error. Resp is ' + resp.text)
    raise AuthError('wrong captcha for ' + str(RETRY) + ' times!')

if __name__ == '__main__':
    RETRY = 3
    TIMEOUT = 60
    for i in range(RETRY, 0, -1):
        try:
            if login():
                title = '心动日剧：登陆成功'
                report(title)
                break
        except Exception as err:
            title = "心动日剧：登陆失败！remain=" + str(i-1)
            content = str(type(err).__name__ + '\n' + str(err))
            report(title, content)
            time.sleep(TIMEOUT)


