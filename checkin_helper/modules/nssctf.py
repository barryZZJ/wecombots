import loguru
import requests as r

from checker import BaseChecker, CheckError

# 登录只在前端做验证，后端可以直接post绕过
# 只要带sessionid和token两个cookie，然后直接post /clockin 就行了
url_login = 'https://www.nssctf.cn/api/user/login/'
url_checkin = 'https://www.nssctf.cn/api/user/clockin/'

class NssctfChecker(BaseChecker):
    def __init__(self, retry: int = 3, timeout: int = 60, conf: dict = None):
        super().__init__('NSSCTF', retry, timeout, conf)
        self.s = r.Session()

    def _prepare(self, context: dict, *args, **kwargs):
        credential = {
            'username': self.conf['username'],
            'password': self.conf['password'],
            'remember': "1"
        }
        resp = self.s.post(url_login, json=credential)
        try:
            js = resp.json()
        except r.JSONDecodeError:
            raise CheckError('json解析失败', resp.text)
        if js['code'] != 200:
            raise CheckError('登录失败', resp.text)
        try:
            token = js['data']['token']
        except KeyError:
            raise CheckError('未找到token', js)
        self.s.cookies.update({'token': token})

    def _check(self, context: dict, *args, **kwargs):
        resp = self.s.post(url_checkin)
        if resp.status_code != 200:
            raise CheckError('签到失败', resp.text)
        try:
            js = resp.json()
        except r.JSONDecodeError:
            raise CheckError('json解析失败', resp.text)
        if js['code'] == 200:
            msg = '签到成功！已连续签到' + js['data'] + '天'
            res = 0
        elif js['code'] == 201:
            msg = '已签到过'
            res = 1
        elif js['code'] == 402:
            msg = '未登录'
            res = -1
        else:
            msg = f"未知返回结果：{js}"
            res = -1
        loguru.logger.info(msg)
        if res == -1:
            raise CheckError('签到失败', msg)
        return msg

    def _finally(self, context: dict, *args, **kwargs):
        self.s.close()
