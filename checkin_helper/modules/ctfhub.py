import time

import loguru
import requests as r
from PIL import Image
from utils.fuckcaptcha import init_ocr, get_threshold_color, fuckcaptcha, dataurl_to_img
from checker import BaseChecker, CheckError
from utils.hashing import md5

url_getcookie = 'https://api.ctfhub.com/User_API/Other/getCookie'
url_login = 'https://api.ctfhub.com/User_API/User/Login'
url_captcha = 'https://api.ctfhub.com/User_API/User/getCaptcha'
url_checkin = 'https://api.ctfhub.com/User_API/User/checkIn'

class CtfhubChecker(BaseChecker):
    def __init__(self, retry: int = 3, timeout: int = 60, conf: dict = None):
        super().__init__('CTFHub', retry, timeout, conf)
        self.s = r.Session()
        ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        self.s.headers.update({
            'User-Agent': ua,
            'Referer': 'https://www.ctfhub.com/',
            'Origin': 'https://www.ctfhub.com/',
        })
        for key, val in self.conf['cookies'].items():
            self.s.cookies.set(key, val.encode('unicode_escape').decode('utf8'))

    def get_capthca(self) -> Image.Image:
        resp = self.s.post(url_captcha, data='{}', verify=False)
        try:
            js = resp.json()
        except r.JSONDecodeError:
            raise CheckError('json解析失败', resp.text)
        if not js['status']:
            raise CheckError('获取验证码失败', js)
        dataurl = js['data']['captcha']
        img = dataurl_to_img(dataurl)
        return img

    def preprocess_img(self, img: Image.Image, aa=True):
        """发现验证码文字大部分都是白色的，所以根据直方图寻找阈值，据此进行二值化"""
        img = img.convert('L')  # 灰度化
        total_pixels = img.size[0] * img.size[1]
        t = get_threshold_color(img, total_pixels, 0.05, reverse=True)
        img = img.point(lambda x: 0 if x < t else 255)  # 二值化
        if aa:
            img = img.resize((img.width * 2, img.height * 2), Image.Resampling.LANCZOS)
            img = img.resize((img.width // 2, img.height // 2), Image.Resampling.LANCZOS)
        return img

    def _prepare(self, context: dict, *args, **kwargs):
        # self.s.post(url_getcookie, verify=False)  # get session id
        self.s.headers.update({
            # 'Authorization': 'ctfhub_sessid='+self.s.cookies['ctfhub_sessid']
            'Authorization': 'ctfhub_sessid='+self.conf['ctfhub_sessid']
        })
        # init_ocr()
        # while True:
        #     captcha_img = self.get_capthca()
        #     captcha_img = self.preprocess_img(captcha_img)
        #     captcha = fuckcaptcha(captcha_img)
        #     if len(captcha) == 4:
        #         break
        #     time.sleep(0.1)
        # credential = {
        #     'account': self.conf['username'],
        #     'password': md5(self.conf['password']),
        #     'remember_me': True,
        #     'captcha': captcha
        # }
        # resp = self.s.post(url_login, json=credential, verify=False)
        # try:
        #     js = resp.json()
        # except r.JSONDecodeError:
        #     raise CheckError('json解析失败', resp.text)
        # if not js['status']:
        #     raise CheckError('登录失败', js['msg'])

    def _check(self, context: dict, *args, **kwargs):
        resp = self.s.post(url_checkin, data='{}', verify=False)
        if resp.status_code != 200:
            raise CheckError('签到失败', resp.text)
        try:
            js = resp.json()
        except r.JSONDecodeError:
            raise CheckError('json解析失败', resp.text)
        if js['status']:
            msg = js['msg']
            res = 0
        elif '已经签到' in js['msg']:
            msg = js['msg']
            res = 1
        else:
            msg = resp.text
            res = -1
        loguru.logger.info(msg)
        if res == -1:
            raise CheckError('签到失败', msg)
        return msg

    def _finally(self, context: dict, *args, **kwargs):
        self.s.close()

if __name__ == '__main__':
    pass
    # import time
    # from config import load_conf
    # from utils.fuckcaptcha import fuckcaptcha
    # conf = load_conf()
    #
    # checker = CtfhubChecker(3, 60, conf['ctfhub'])
    #
    # for _ in range(10):
    #     while True:
    #         captcha_img = checker.get_capthca()
    #         captcha_img = checker.preprocess_img(captcha_img, False)
    #         captcha_img_aa = checker.preprocess_img(captcha_img, True)
    #         captcha = fuckcaptcha(captcha_img)
    #         captcha_aa = fuckcaptcha(captcha_img_aa)
    #         if len(captcha) == 4 or len(captcha_aa) == 4:
    #             break
    #         time.sleep(0.1)
    #     with open(f'LANCZOS/{_}.{captcha}.png', 'wb') as f:
    #         captcha_img.save(f, format='png')
    #     with open(f'LANCZOS/{_}.AA_{captcha_aa}.png', 'wb') as f:
    #         captcha_img_aa.save(f, format='png')
    #     time.sleep(0.1)