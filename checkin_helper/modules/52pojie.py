import requests

# from checker import BaseChecker, CheckError

# TODO 用不了，开了js反爬，只能selenium实现。
def sign_52pojie(cookie):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 Edg/103.0.1264.77',
        'Cookie': cookie,
    }
    # 申请签到
    apply_url = 'https://www.52pojie.cn/home.php?mod=task&do=apply&id=2&referer=%2F'
    apply_req = requests.post(apply_url, headers=headers, allow_redirects=False)
    if '登录或注册' in apply_req.text:
        mes = '签到失败，cookie可能失效，请检查更新。'
    else:
        # 进行签到
        sign_url = 'https://www.52pojie.cn/home.php?mod=task&do=draw&id=2'
        sign_req = requests.post(sign_url, headers=headers)
        # 任务已完成
        if '任务已完成' in sign_req.text:
            # print('签到成功！')
            mes = '签到成功'
        # 不是进行中的任务
        elif '不是进行中的任务' in sign_req.text:
            # print('已经签到过了.')
            mes = '今天已经签到过了！'
        else:
            print('wuaipojie:', sign_req.text)
            mes = '签到失败，请联系管理员，提交错误信息！'
    return mes


# class W52PojieChecker(BaseChecker):
#     def __init__(self, retry: int = 1, timeout: int = 60, *, cookie):
#         super().__init__('吾爱破解', retry, timeout)
#         self.cookie = cookie
#
#     def _check(self, context: dict, *args, **kwargs):
#         mes = sign_52pojie(self.cookie)
#         if mes != '签到成功':
#             raise CheckError('签到失败', mes)

if __name__ == '__main__':
    res = sign_52pojie('htVC_2132_connect_is_bind=0; htVC_2132_smile=1D1; KF4=T6LNJz; htVC_2132_nofavfid=1; htVC_2132_saltkey=X4Aw7ZA9; htVC_2132_lastvisit=1689998219; htVC_2132_auth=ed02EdJ906GybaDT4YlyWUJHCDKHoTBShkGHG8UK45T7BzOkn%2F7WVJmWi2%2FY4BZpyX1It%2BcEur3UL0lpauSCn62Osjcp; wzws_sessionid=gDE4My4yNDIuMjU0LjE2OKBkv0msgmRiMWNhYYExNWMyZjY=; htVC_2132_sid=0; htVC_2132_noticonf=1826801D1D3_3_1; htVC_2132_ulastactivity=1690271089%7C0; htVC_2132_lastcheckfeed=1826801%7C1690271091; htVC_2132_st_p=1826801%7C1690271093%7C116623d0fcd2bc8bab67b0ce3cda8a09; htVC_2132_visitedfid=24D2D4D73D8; htVC_2132_viewid=tid_1677080; htVC_2132_lastact=1690275091%09plugin.php%09')
    print(res)
