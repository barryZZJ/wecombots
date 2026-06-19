import contextlib
import os.path
import time
from io import BytesIO
import json

import loguru
from PIL import Image
from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.proxy import Proxy, ProxyType


from checker import BaseChecker, CheckError
from OrderClickCaptchaSolver.fuckorderclickcaptcha import fuck_orderclick_captcha

# 0 10 * * * python3 ~/yuyuncheckin/main.py

url_login = 'https://app.rainyun.com/auth/login'
url_dashboard = 'https://app.rainyun.com/dashboard'
url_points = 'https://app.rainyun.com/account/reward/earn'
COOKIE_PATH = os.path.join(os.path.dirname(__file__), 'cookies.json')

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

    # proxycap = genProxyCap()
    # proxycap = None
    # browser = webdriver.Chrome(options=opt, desired_capabilities=proxycap)
    browser = webdriver.Chrome(options=opt)
    browser.implicitly_wait(30)
    wait = WebDriverWait(browser, 30)
    return browser, wait

@contextlib.contextmanager
def iframe_switch(browser, wait, iframe_id: str):
    iframe_captcha = wait.until(lambda browser: browser.find_element(By.ID, iframe_id))
    browser.switch_to.frame(iframe_captcha)
    yield
    browser.switch_to.default_content()

def merge_images(bg, char):
    bg_image = Image.open(BytesIO(bg))
    char_image = Image.open(BytesIO(char))

    new_size = (bg_image.width, bg_image.height + char_image.height)
    merged = Image.new('RGB', new_size, (0, 0, 0, 255))
    merged.paste(bg_image, (0, 0))
    merged.paste(char_image, (0, bg_image.height))

    return merged

def save_cookies(browser: webdriver.Chrome, path: str):
    cookies = browser.get_cookies()
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(cookies, f, ensure_ascii=False, indent=4)


def load_cookies(browser: webdriver.Chrome, path: str):
    if not os.path.exists(path):
        loguru.logger.warning(f"Cookie file {path} does not exist.")
        return False
    with open(path, 'r', encoding='utf-8') as f:
        cookies = json.load(f)
    for cookie in cookies:
        # Ensure the cookie has the necessary attributes
        if 'name' in cookie and 'value' in cookie:
            # Add the cookie to the browser
            browser.add_cookie(cookie)
        else:
            loguru.logger.warning(f"Skipping invalid cookie: {cookie}")
    return True

class YuyunCheckerV2(BaseChecker):
    def __init__(self, retry: int = 3, timeout: int = 60, conf: dict = None):
        super().__init__('雨云', retry, timeout, conf)

    def login(self):
        # 登陆
        self.browser.get(url_login)
        # load_cookies(self.browser, COOKIE_PATH)
        # self.browser.get(url_points)
        # # print(self.browser.page_source)
        # # print(self.browser.current_url)
        # try:
        #     # cookie 登录
        #     WebDriverWait(self.browser, 5).until(lambda browser: 'login' in browser.current_url)
        #     loguru.logger.warning('Cookie未登录或已过期，重新登录')
        # except TimeoutException:
        #     loguru.logger.info('Cookie登录成功')
        #     self._save_screenshot()
        #     return
        # print(browser.page_source)
        ele_usr = self.wait.until(lambda browser: browser.find_element(By.CSS_SELECTOR, "input[type='text']"))
        ele_pss = self.browser.find_element(By.CSS_SELECTOR, "input[type='password']")
        # ele_rem = browser.find_element(By.CSS_SELECTOR, "#remember-me+label")
        ele_sub = self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        ele_usr.send_keys(self.conf['username'])
        self.wait.until(lambda browser: ele_usr.get_attribute('value') == self.conf['username'])  # 等待输入框填入用户名
        ele_pss.send_keys(self.conf['password'])
        self.wait.until(lambda browser: ele_pss.get_attribute('value') == self.conf['password'])
        time.sleep(1)
        # ele_rem.click()
        ele_sub.click()
        self.wait.until(lambda browser: 'dashboard' in browser.current_url)  # 不等的话下面的url访问后会再回到dashboard
        save_cookies(self.browser, COOKIE_PATH)


    def checkin(self):
        # 打卡
        res = -1

        ele_checkin = self.find_ele_checkin()
        if not ele_checkin:
            msg = '未找到签到按钮'
        elif ele_checkin.text == '已完成':
            msg = '已签到过'
            res = 1
        elif ele_checkin.text == '领取奖励':
            ele_checkin.click()
            retry = 3
            while not self.try_solve_captcha():
                retry -= 1
                if retry <= 0:
                    msg = '验证码验证失败'
                    return msg, res
                loguru.logger.debug('验证码验证失败，重试')
                self.find_ele_checkin()
            ele_checkin = self.find_ele_checkin()
            if ele_checkin and ele_checkin.text == '已完成':
                msg = '签到成功！'
                res = 0
            else:
                msg = '点击签到按钮后出现未预料结果'
        else:
            msg = '未知按钮名：' + ele_checkin.text
        return msg, res

    def find_ele_checkin(self):
        # print(self.browser.current_url)
        # self._save_screenshot('find_checkin')
        self.browser.get(url_points)
        ele_tab = self.wait.until(lambda browser: browser.find_element(By.CSS_SELECTOR, 'div[role="tablist"]'))
        ele_checkin = None

        ele_cards = ele_tab.find_elements(By.CLASS_NAME, 'card')
        for ele_card in ele_cards:
            ele_txt = ele_card.find_element(By.TAG_NAME, 'span')
            if ele_txt.text.strip() == '每日签到':
                ele_checkin = ele_txt.find_element(By.XPATH, 'following-sibling::*')
                break
        return ele_checkin

    def find_captcha(self):
        # make sure called in captcha iframe
        ele_bg: WebElement = self.browser.find_element(By.ID, 'slideBg')
        url = WebDriverWait(self.browser, 30, 5).until(lambda browser: browser.execute_script("return window.getComputedStyle(arguments[0]).backgroundImage;", ele_bg) != 'none')
        time.sleep(1)
        ele_char: WebElement = self.browser.find_element(By.CSS_SELECTOR, '#instruction img')
        ele_confirm: WebElement = self.browser.find_element(By.CSS_SELECTOR, '#tcStatus div[role="button"]')

        bg = ele_bg.screenshot_as_png
        char = ele_char.screenshot_as_png
        captcha = merge_images(bg, char)
        return ele_bg, ele_char, ele_confirm, captcha

    def solve_captcha(self, ele_bg, xyxys, ele_confirm):
        # make sure called in captcha iframe
        size = ele_bg.size
        action = ActionChains(self.browser)
        for xyxy in xyxys:
            offset_x = (xyxy[0] + xyxy[2]) / 2 - size['width'] / 2
            offset_y = (xyxy[1] + xyxy[3]) / 2 - size['height'] / 2
            action.move_to_element_with_offset(ele_bg, offset_x, offset_y).click().pause(0.1).perform()
        action.click(ele_confirm)
        action.perform()

    def reload_captcha(self, ele_bg):
        old_bg_url = self.browser.execute_script("return window.getComputedStyle(arguments[0]).backgroundImage;",
                                                 ele_bg)
        self.browser.find_element(By.ID, 'reload').click()
        # TODO: this will raise TimeoutException for some reason
        self.wait.until(
            lambda browser: self.browser.execute_script("return window.getComputedStyle(arguments[0]).backgroundImage;",
                                                        ele_bg) != old_bg_url)

    def try_solve_captcha(self):
        # from OrderClickCaptchaSolver.utils.utils import draw_img
        # switch to captcha iframe
        try:
            with iframe_switch(self.browser, self.wait, 'tcaptcha_iframe_dy'):
                ele_bg, ele_char, ele_confirm, captcha = self.find_captcha()
                xyxys = fuck_orderclick_captcha(captcha)
                loguru.logger.debug('solve_captcha xyxys: ' + str(xyxys))
                # captcha.save('captcha.jpg')
                # draw_img('captcha.jpg', xyxys, 'res.jpg')
                self.solve_captcha(ele_bg, xyxys, ele_confirm)
            WebDriverWait(self.browser, 10, 5, ignored_exceptions=[NoSuchElementException]) \
                .until_not(lambda browser: browser.find_element(By.ID, 't_mask'))
            # solve captcha success
            return True
        except TimeoutException:
            loguru.logger.debug('solve captcha failed')
            return False

    def _save_screenshot(self, name='yuyunv2'):
        screenshot_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), f'{name}-{time.strftime("%Y%m%d-%H%M%S")}.png'))
        self.browser.save_screenshot(screenshot_path)
        loguru.logger.error('已保存截图到：' + screenshot_path)
        return screenshot_path

    def _prepare(self, context: dict, *args, **kwargs):
        self.browser: webdriver.Chrome
        self.wait: WebDriverWait
        self.browser, self.wait = initbrowser()

    def _on_error(self, context: dict, *args, **kwargs):
        self._save_screenshot()

    def _check(self, context: dict, *args, **kwargs):
        try:
            self.login()
        except Exception as err:
            raise CheckError('第一步登录失败！', str(err))

        try:
            msg, res = self.checkin()
            if res == -1:
                raise CheckError('第二步签到失败', msg)
            return msg
        except Exception as err:
            content = str(type(err).__name__) + '\n' + str(err)
            raise CheckError('第二步签到失败', content)

    def _finally(self, context: dict, *args, **kwargs):
        self.browser.close()
        self.browser.quit()
