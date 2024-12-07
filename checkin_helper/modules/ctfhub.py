import itertools

import loguru
import requests as r
from PIL import Image

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

    def get_capthca(self) -> Image.Image:
        from utils.fuckcaptcha import dataurl_to_img
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

    @staticmethod
    def get_threshold(hist, total_pixels, percent):
        for pixel, cum_count in enumerate(itertools.accumulate(hist)):
            if cum_count >= total_pixels * percent:
                return pixel
        return 255

    def preprocess_img(self, img: Image.Image):
        """发现验证码文字大部分都是白色的，所以根据直方图寻找阈值，据此进行二值化"""
        img = img.convert('L')  # 灰度化
        hist = img.histogram()
        total_pixels = img.size[0] * img.size[1]
        t = 255 - self.get_threshold(hist[::-1], total_pixels, 0.05)
        img = img.point(lambda x: 0 if x < t else 255)  # 二值化
        return img

    def _prepare(self, context: dict, *args, **kwargs):
        self.s.post(url_getcookie, verify=False)  # get session id
        self.s.headers.update({
            'Authorization': 'ctfhub_sessid='+self.s.cookies['ctfhub_sessid']
        })
        from utils.fuckcaptcha import fuckcaptcha
        captcha_img = self.get_capthca()
        captcha_img = self.preprocess_img(captcha_img)
        captcha = fuckcaptcha(captcha_img)
        credential = {
            'account': self.conf['username'],
            'password': md5(self.conf['password']),
            'remember_me': True,
            'captcha': captcha
        }
        resp = self.s.post(url_login, json=credential, verify=False)
        try:
            js = resp.json()
        except r.JSONDecodeError:
            raise CheckError('json解析失败', resp.text)
        if not js['status']:
            raise CheckError('登录失败', js['msg'])

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
