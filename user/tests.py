from django.test import TestCase, Client
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
from user.models import WebCase, CheckWebCase

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


# 前端单元测试操作
def webCase(url, oprates):
    driver = webdriver.Chrome()
    driver.implicitly_wait(15)
    driver.maximize_window()
    driver.get(url)
    wait = WebDriverWait(driver, 15)
    # 测试结果
    data = {'errcode': 0, 'errmsg': 'ok'}
    text = ''
    print(oprates)

    # 操作前端页面
    try:
        for oprate in oprates['test']:
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
        data['errcode'] = 101
        data['errmsg'] = '获取元素异常，请检查CSS参数'
        driver.quit()
        return data

    # 验证文本
    try:
        for oprate in oprates['check']:
            element = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, oprate['css'])),
                message='找不到元素-%s' % (oprate['css']))
            method = getattr(element, oprate['method'])
            if oprate['param']:
                text = method(oprate['param'])
            else:
                text = method()
            sleep(1)
            print(text)
            print(oprate['checktext'])
            if text != oprate['checktext']:
                data['errcode'] = 102
                data['errmsg'] = '验证数据不一致'
                driver.quit()
                return data

    except Exception as e:
        print(e)
        data['errcode'] = 103
        data['errmsg'] = '获取文本异常,请检查参照参数'
        driver.quit()
        return data

    driver.quit()
    return data


# 前端整体测试
def webTest(url, webTypes):
    driver = webdriver.Chrome()
    driver.implicitly_wait(15)
    driver.maximize_window()
    driver.get(url)
    wait = WebDriverWait(driver, 15)
    # 测试结果
    data = {'errcode': 0, 'errmsg': 'ok'}
    text = ''
    print(webTypes)

    for webType in webTypes:
        if webType['is_test']:
            # 操作前端页面
            webCases = WebCase.objects.filter(testType=webType['id'])
            for webCase in webCases:
                try:
                    element = wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, webCase.webcss)),
                        message='找不到元素-%s' % (webCase.webcss))
                    method = getattr(element, webCase.weboprate)
                    if webCase.webparam:
                        print(webCase.webparam)
                        method(webCase.webparam)
                    else:
                        method()
                        sleep(1)
                except Exception as e:
                    print(e)
                    data['errcode'] = 101
                    data['errmsg'] = '获取元素异常，请检查CSS参数'
                    driver.quit()
                    return data

            # 验证文本
            checkWebCases = CheckWebCase.objects.filter(testType=webType['id'])
            for checkWebCase in checkWebCases:
                try:
                    element = wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, checkWebCase.webcss)),
                        message='找不到元素-%s' % (checkWebCase.webcss))
                    method = getattr(element, checkWebCase.weboprate)
                    if checkWebCase.webparam:
                        text = method(checkWebCase.webparam)
                    else:
                        text = method()
                    sleep(1)
                    print(text)
                    print(checkWebCase.checktext)
                    if text != checkWebCase.checktext:
                        data['errcode'] = 102
                        data['errmsg'] = '验证数据不一致'
                        driver.quit()
                        return data

                except Exception as e:
                    print(e)
                    data['errcode'] = 103
                    data['errmsg'] = '获取数据异常,请检查CSS参数'
                    driver.quit()
                    return data

    driver.quit()
    return data


if __name__ == '__main__':
    webCase()
