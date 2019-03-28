from django.test import TestCase, Client
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep

# Create your tests here.


class DemoTest(TestCase):
    def test(self):
        client = Client()
        response = client.post('http://127.0.0.1:8000/v1/login/', {
            "email": "linzhifu222@163.com",
            "password": "123"
        })
        print(response.content)
        self.assertEqual(True, True)


# 前端单元测试
def webCase(url, oprates):
    # url = 'https://mpstest.longsys.com/'
    # oprates = [{
    #     'css': '.way li:nth-of-type(2)',
    #     'method': 'click',
    #     'param': '',
    # },
    #            {
    #                'css': '.password-login .mail .el-input__inner',
    #                'method': 'send_keys',
    #                'param': '18129832245@163.com',
    #            },
    #            {
    #                'css': '.password-login .password .el-input__inner',
    #                'method': 'send_keys',
    #                'param': '123',
    #            },
    #            {
    #                'css': '.password-login .login',
    #                'method': 'click',
    #                'param': '',
    #            }]
    driver = webdriver.Chrome()
    driver.implicitly_wait(30)
    driver.maximize_window()
    driver.get(url)
    wait = WebDriverWait(driver, 30)

    try:
        for oprate in oprates:
            element = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, oprate['css'])),
                message='找不到元素-%s' % (oprate['css']))
            method = getattr(element, oprate['method'])
            if oprate['param']:
                method(oprate['param'])
            else:
                method()
            sleep(1)
    except Exception as e:
        print(e)

    finally:
        driver.quit()


if __name__ == '__main__':
    webCase()
