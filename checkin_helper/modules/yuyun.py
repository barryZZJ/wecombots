import time

import requests as r
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.proxy import Proxy, ProxyType


from checker import BaseChecker, CheckError
# 0 10 * * * python3 ~/yuyuncheckin/main.py

url_login = 'https://app.rainyun.com/auth/login'
url_points = 'https://app.rainyun.com/account/reward/earn'
USER = 'barry'
PASS = 'zzjzzj0123'


# KEY = 'SCT164400THDN7R51ck5uOz8H3MAhIejfR'

# def push(key, title, content=None):
#     url = 'https://sctapi.ftqq.com/{}.send'.format(key)
#     params = {
#         'title': title
#     }
#     if content:
#         params['content'] = content
#     with httpRequestUtil_contextmanager.httpRequest(r.Session(), url, 'get', params) as resp:
#         pass

def genProxyCap():
    prox = Proxy()
    prox.proxy_type = ProxyType.MANUAL
    prox.http_proxy = "127.0.0.1:10809"
    prox.ssl_proxy = "127.0.0.1:10809"
    capabilities = webdriver.DesiredCapabilities.CHROME
    prox.add_to_capabilities(capabilities)
    return capabilities


def initbrowser():
    opt = webdriver.ChromeOptions()
    opt.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36')
    opt.add_argument('--headless')  # 无界面
    opt.add_argument('--no-sandbox')
    opt.add_argument('--disable-dev-shm-usage')

    proxycap = genProxyCap()
    proxycap = None
    browser = webdriver.Chrome(options=opt, desired_capabilities=proxycap)
    browser.implicitly_wait(30)
    wait = WebDriverWait(browser, 30)
    return browser, wait


def login(browser, wait):
    # 登陆
    browser.get(url_login)
    print(browser.page_source)
    ele_usr = wait.until(lambda browser: browser.find_element(By.CSS_SELECTOR, "input[type='text']"))
    ele_pss = browser.find_element(By.CSS_SELECTOR, "input[type='password']")
    # ele_rem = browser.find_element(By.CSS_SELECTOR, "#remember-me+label")
    ele_sub = browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
    ele_usr.send_keys(USER)
    ele_pss.send_keys(PASS)
    # ele_rem.click()
    ele_sub.click()
    wait.until(lambda browser: 'dashboard' in browser.current_url)  # 不等的话下面的url访问后会再回到dashboard


def checkin(browser, wait):
    # 打卡
    res = -1

    def find_ele_checkin():
        browser.get(url_points)
        ele_tab = browser.find_element(By.CSS_SELECTOR, 'div[role="tablist"]')
        ele_checkin = None

        ele_cards = ele_tab.find_elements(By.CLASS_NAME, 'card')
        for ele_card in ele_cards:
            ele_txt = ele_card.find_element(By.TAG_NAME, 'span')
            if ele_txt.text.strip() == '每日签到':
                ele_checkin = ele_txt.find_element(By.XPATH, 'following-sibling::*')
                break
        return ele_checkin

    ele_checkin = find_ele_checkin()
    if not ele_checkin:
        msg = '未找到签到按钮'
    elif ele_checkin.text == '已完成':
        msg = '已签到过'
        res = 1
    elif ele_checkin.text == '领取奖励':
        ele_checkin.click()
        # assert click result
        ele_checkin = find_ele_checkin()
        if ele_checkin and ele_checkin.text == '已完成':
            msg = '签到成功！'
            res = 0
        else:
            msg = '点击按钮后出现未预料结果'
    else:
        msg = '未知按钮名：' + ele_checkin.text
    return msg, res


class YuyunChecker(BaseChecker):
    def __init__(self, retry: int = 3, timeout: int = 60):
        super().__init__('雨云', retry, timeout)

    def _prepare(self, context: dict, *args, **kwargs):
        browser, wait = initbrowser()
        context.update(dict(
            browser=browser,
            wait=wait
        ))

    def _check(self, context: dict, *args, **kwargs):
        browser = context['browser']
        wait = context['wait']
        try:
            login(browser, wait)
        except Exception as err:
            raise CheckError('第一步登录失败！', str(err))

        try:
            msg, res = checkin(browser, wait)
            if res != -1:
                raise CheckError('第二步签到失败', msg)
        except Exception as err:
            content = str(type(err).__name__) + '\n' + str(err)
            raise CheckError('第二步签到失败', content)

    def _finally(self, context: dict, *args, **kwargs):
        browser = context['browser']
        browser.close()
        browser.quit()
