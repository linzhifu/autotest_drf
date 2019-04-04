from django.test import TestCase, Client
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
from user.models import WebCase, CheckWebCase, TestRecord, ApiCase
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
import logging
from datetime import datetime
import os
import requests
import time
import json

# Create your tests here.

# 日子打印配置
logging.basicConfig(
    level=logging.DEBUG, format='%(asctime)s-%(levelname)s-%(message)s')
logging.disable(logging.DEBUG)

# token配置
config = {
    'userid': '',
    'token': '',
}

# 用户登陆配置
loginCase = {
    'method': 'post',
    'url': '/api/v1/user/login',
    'params': {},
    'json': {
        'email': '18129832245@163.com',
        'pswmd5': '202cb962ac59075b964b07152d234b70',
        'timestamp': int(time.time())
    },
    'response': {
        'errcode': '0',
        'errmsg': 'ok'
    }
}


# 记录测试log装饰器
def save_log(fuc):
    def wrapper(*args, **kwargs):
        testName = kwargs.get('testName')
        testType = kwargs.get('type')
        # 测试目录
        logData = datetime.now().strftime('%Y-%m-%d')
        logType = logData + '\\' + testType
        LOGDIR = logType + '\\' + testName

        # 检查目录
        if os.path.exists(logData):
            pass
        else:
            os.mkdir(logData)

        if os.path.exists(logType):
            pass
        else:
            os.mkdir(logType)

        if os.path.exists(LOGDIR):
            pass
        else:
            os.mkdir(LOGDIR)

        # LOG文件名
        logName = datetime.now().strftime('%Y%m%d%H%M%S')

        # 保存路径
        savePath = LOGDIR + '\\' + '%s.log' % (logName)

        # 指定logger输出格式
        logger = logging.getLogger()
        formatter = logging.Formatter('%(asctime)s-%(levelname)s-%(message)s')

        # DEBUG输出保存测试LOG
        file_handler = logging.FileHandler(savePath)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)

        logger.addHandler(file_handler)

        resu = fuc(*args, **kwargs)

        # 保存测试LOG
        logger.removeHandler(file_handler)
        file_handler.close()
        if not resu.get('errcode'):
            os.rename(savePath,
                      LOGDIR + '\\' + '%s-%s.log' % (logName, 'pass'))
        else:
            os.rename(savePath,
                      LOGDIR + '\\' + '%s-%s.log' % (logName, 'fail'))
        return resu

    return wrapper


# django测试示例
class DemoTest(TestCase):
    def test(self):
        client = Client()
        response = client.post('http://127.0.0.1:8000/v1/login/', {
            "email": "linzhifu222@163.com",
            "password": "123"
        })
        print(response.content)
        self.assertEqual(True, True)


# 添加一次测试记录
def add_one_test_record(object, resu):
    test_time = timezone.now().date()
    content_type = ContentType.objects.get_for_model(object)
    test_record, _ = TestRecord.objects.get_or_create(
        content_type=content_type, object_id=object.pk, test_time=test_time)
    test_record.test_all += 1
    if resu:
        test_record.test_pass += 1
    else:
        test_record.test_fail += 1
    test_record.save()


# # 获取测试记录
# def get_record(object):
#     today = timezone.now().date()
#     test_times = []
#     test_all = []
#     test_pass = []
#     test_fail = []
#     for i in range(6, -1, -1):
#         test_time = today - datetime.timedelta(days=i)
#         test_times.append(test_time.strftime('%m/%d'))
#         content_type = ContentType.objects.get_for_model(object)
#         test_record, _ = TestRecord.objects.get_or_create(
#             content_type=content_type,
#             object_id=object.pk,
#             test_time=test_time)
#         test_all.append(test_record.test_all)
#         test_pass.append(test_record.test_pass)
#         test_fail.append(test_record.test_fail)
#     return test_times, test_all, test_pass, test_fail


# 前端单元测试操作
def webCase(url, host, webType, webManager):
    try:
        desired_capabilities = {'platform': 'WINDOWS', 'browserName': 'chrome'}
        driver = webdriver.Remote(
            host, desired_capabilities=desired_capabilities)
    except Exception:
        opt = webdriver.ChromeOptions()
        opt.set_headless()
        # 谷歌文档提到需要加上这个属性来规避bug
        opt.add_argument('--disable-gpu')
        # 指定浏览器分辨率
        opt.add_argument('window-size=1920x3000')
        driver = webdriver.Chrome(options=opt)
    driver.implicitly_wait(15)
    driver.maximize_window()
    driver.get(url)
    wait = WebDriverWait(driver, 15)
    # 测试结果
    data = {'errcode': 0, 'errmsg': 'ok'}
    text = ''

    # 操作前端页面
    webCases = WebCase.objects.filter(testType=webType.id)
    for webCase in webCases:
        try:
            element = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, webCase.webcss)),
                message='找不到元素-%s' % (webCase.webcss))
            method = getattr(element, webCase.weboprate)
            if webCase.webparam:
                method(webCase.webparam)
            else:
                method()
                sleep(1)
        except Exception as e:
            print(webCase.webname + ' ：' + str(e))
            webType.result = False
            webType.save()
            add_one_test_record(webType, False)
            webManager.result = False
            webManager.save()
            data['errcode'] = 101
            data['errmsg'] = webCase.webname + ' ：' + str(e)
            driver.quit()
            logging.info(webType.typename + '-FAIL')
            return data

    # 验证文本
    checkWebCases = CheckWebCase.objects.filter(testType=webType.id)
    for checkWebCase in checkWebCases:
        try:
            element = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                                            checkWebCase.webcss)),
                message='找不到元素-%s' % (checkWebCase.webcss))
            method = getattr(element, checkWebCase.weboprate)
            if checkWebCase.webparam:
                text = method(checkWebCase.webparam)
            else:
                text = method()
            sleep(1)
            if text != checkWebCase.checktext:
                webType.result = False
                webType.save()
                add_one_test_record(webType, False)
                webManager.result = False
                webManager.save()
                data['errcode'] = 102
                data['errmsg'] = checkWebCase.webname \
                    + '：' + checkWebCase.checktext + ' != ' + text
                driver.quit()
                logging.info(webType.typename + '-FAIL')
                return data

        except Exception as e:
            print(checkWebCase.webname + ' ：' + str(e))
            webType.result = False
            webType.save()
            add_one_test_record(webType, False)
            webManager.result = False
            webManager.save()
            data['errcode'] = 103
            data['errmsg'] = checkWebCase.webname + ' ：' + str(e)
            driver.quit()
            logging.info(webType.typename + '-FAIL')
            return data

    webType.result = True
    webType.save()
    add_one_test_record(webType, True)
    logging.info(webType.typename + '-PASS')

    driver.quit()
    return data


# 前端整体测试
@save_log
def webTest(url, host, webTypes, webManager, testName, type):
    try:
        desired_capabilities = {'platform': 'WINDOWS', 'browserName': 'chrome'}
        driver = webdriver.Remote(
            host, desired_capabilities=desired_capabilities)
    except Exception:
        opt = webdriver.ChromeOptions()
        opt.set_headless()
        # 谷歌文档提到需要加上这个属性来规避bug
        opt.add_argument('--disable-gpu')
        # 指定浏览器分辨率
        opt.add_argument('window-size=1920x3000')
        driver = webdriver.Chrome(options=opt)
    # driver = webdriver.Chrome()
    driver.implicitly_wait(15)
    driver.maximize_window()
    driver.get(url)
    wait = WebDriverWait(driver, 15)
    # 测试结果
    data = {'errcode': 0, 'errmsg': 'ok'}
    text = ''

    for webType in webTypes:
        if webType.is_test:
            # 操作前端页面
            webCases = WebCase.objects.filter(testType=webType.id)
            for webCase in webCases:
                try:
                    element = wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                    webCase.webcss)),
                        message='找不到元素-%s' % (webCase.webcss))
                    method = getattr(element, webCase.weboprate)
                    if webCase.webparam:
                        method(webCase.webparam)
                    else:
                        method()
                        sleep(1)
                except Exception as e:
                    print(webCase.webname + ' ：' + str(e))
                    webType.result = False
                    webType.save()
                    webManager.result = False
                    webManager.save()
                    add_one_test_record(webType, False)
                    add_one_test_record(webManager, False)
                    data['errcode'] = 101
                    data['errmsg'] = webCase.webname + ' ：' + str(e)
                    driver.quit()
                    logging.info(webType.typename + '-FAIL')
                    return data

            # 验证文本
            checkWebCases = CheckWebCase.objects.filter(testType=webType.id)
            for checkWebCase in checkWebCases:
                try:
                    element = wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                    checkWebCase.webcss)),
                        message='找不到元素-%s' % (checkWebCase.webcss))
                    method = getattr(element, checkWebCase.weboprate)
                    if checkWebCase.webparam:
                        text = method(checkWebCase.webparam)
                    else:
                        text = method()
                    sleep(1)
                    if text != checkWebCase.checktext:
                        webType.result = False
                        webType.save()
                        webManager.result = False
                        webManager.save()
                        add_one_test_record(webType, False)
                        add_one_test_record(webManager, False)
                        data['errcode'] = 102
                        data['errmsg'] = checkWebCase.webname \
                            + '：' + checkWebCase.checktext + ' != ' + text
                        driver.quit()
                        logging.info(webType.typename + '-FAIL')
                        return data

                except Exception as e:
                    print(checkWebCase.webname + ' ：' + str(e))
                    webType.result = False
                    webType.save()
                    webManager.result = False
                    webManager.save()
                    add_one_test_record(webType, False)
                    add_one_test_record(webManager, False)
                    data['errcode'] = 103
                    data['errmsg'] = checkWebCase.webname + ' ：' + str(e)
                    driver.quit()
                    logging.info(webType.typename + '-FAIL')
                    return data

            webType.result = True
            webType.save()
            add_one_test_record(webType, True)
            logging.info(webType.typename + '-PASS')

    webManager.result = True
    webManager.save()
    add_one_test_record(webManager, True)
    driver.quit()
    return data


# API请求
def doTest(case, RESTAPI_DOMAIN):
    start = time.time()
    response = ''
    error = None
    try:
        response = requests.request(
            method=case['method'],
            url=RESTAPI_DOMAIN + case['url'],
            params=case['params'],
            json=case['json'],
            verify=False)
    except requests.exceptions.ConnectionError:
        error = "ConnectionError"
    except requests.exceptions.HTTPError:
        error = "HTTPError"
    except requests.exceptions.URLRequired:
        error = "URLRequired"
    except requests.exceptions.TooManyRedirects:
        error = "TooManyRedirects"
    except requests.exceptions.ReadTimeout:
        error = "ReadTimeout"
    except requests.exceptions.InvalidURL:
        error = "InvalidURL"
    timeval = time.time() - start

    rev = ''
    if error is None:
        # rev = json.loads(r.text)
        try:
            rev = response.json()
        except Exception as e:
            error = '返回数据不是JSON对象'

    if error is None:
        if str(rev.get('errcode')) != case['response']['errcode']:
            error = 'errcode不一致'

    # 记录userId和token
    if error is None:
        if rev.get('data'):
            if rev['data'].get('userid') and rev['data'].get('token'):
                config['userid'] = rev['data'].get('userid')
                config['token'] = rev['data'].get('token')
    result = {'time': str(round(timeval, 2)), 'error': error}
    return result


# 后端API单元测试
def apiCase(url, apiType, apiManager):
    data = {'errcode': 0, 'errmsg': 'ok'}
    RESTAPI_DOMAIN = url

    # 先登陆获取token
    doTest(loginCase, RESTAPI_DOMAIN)
    apiCases = ApiCase.objects.filter(testType=apiType.id)
    for apiCase in apiCases:
        # 格式化参数
        case = {}
        try:
            params = json.loads(apiCase.apiparam)
            if params.get('userid') and params.get('token'):
                params['userid'] = config['userid']
                params['token'] = config['token']
        except Exception:
            params = ''
        try:
            body_json = json.loads(apiCase.apijson)
            if body_json.get('timestamp'):
                body_json['timestamp'] = int(time.time())
        except Exception:
            body_json = ''
        try:
            response = json.loads(apiCase.apiresponse)
        except Exception:
            response = ''

        case['method'] = apiCase.apimethod
        case['url'] = apiCase.apiurl
        case['params'] = params
        case['json'] = body_json
        case['response'] = response

        # print(case)
        # 发送请求
        result = doTest(case, RESTAPI_DOMAIN)
        if result['error']:
            data['errcode'] = 101
            data['errmsg'] = apiCase.apiname + '：' + result['error']
            apiCase.result = False
            apiCase.save()
            apiType.result = False
            apiType.save()
            add_one_test_record(apiType, False)
            apiManager.result = False
            apiManager.save()
            logging.info(apiCase.apiname + '-' + apiCase.apiurl + '-' +
                         result['time'] + '-' + 'FAIL')
            return data

        apiCase.result = True
        apiCase.save()
        logging.info(apiCase.apiname + '-' + apiCase.apiurl + '-' +
                     result['time'] + '-' + 'PASS')

    apiType.result = True
    apiType.save()
    add_one_test_record(apiType, True)
    return data


@save_log
# 后端整体测试
def apiTest(url, apiTypes, apiManager, testName, type):
    data = {'errcode': 0, 'errmsg': 'ok'}
    RESTAPI_DOMAIN = url

    # 先登陆获取token
    doTest(loginCase, RESTAPI_DOMAIN)

    for apiType in apiTypes:
        if apiType.is_test:
            apiCases = ApiCase.objects.filter(testType=apiType.id)
            for apiCase in apiCases:
                # 格式化参数
                case = {}
                try:
                    params = json.loads(apiCase.apiparam)
                    if params.get('userid') and params.get('token'):
                        params['userid'] = config['userid']
                        params['token'] = config['token']
                except Exception:
                    params = ''
                try:
                    body_json = json.loads(apiCase.apijson)
                    if body_json.get('timestamp'):
                        body_json['timestamp'] = int(time.time())
                except Exception:
                    body_json = ''
                try:
                    response = json.loads(apiCase.apiresponse)
                except Exception:
                    response = ''

                case['method'] = apiCase.apimethod
                case['url'] = apiCase.apiurl
                case['params'] = params
                case['json'] = body_json
                case['response'] = response

                # print(case)
                # 发送请求
                result = doTest(case, RESTAPI_DOMAIN)
                if result['error']:
                    data['errcode'] = 101
                    data['errmsg'] = apiCase.apiname + '：' + result['error']
                    apiCase.result = False
                    apiCase.save()
                    apiType.result = False
                    apiType.save()
                    apiManager.result = False
                    apiManager.save()
                    add_one_test_record(apiType, False)
                    add_one_test_record(apiManager, False)
                    logging.info(apiCase.apiname + '-' + apiCase.apiurl + '-' +
                                 result['time'] + '-' + 'FAIL')
                    return data

                apiCase.result = True
                apiCase.save()
                logging.info(apiCase.apiname + '-' + apiCase.apiurl + '-' +
                             result['time'] + '-' + 'PASS')

            apiType.result = True
            apiType.save()
            add_one_test_record(apiType, True)

    apiManager.result = True
    apiManager.save()
    add_one_test_record(apiManager, True)
    return data


if __name__ == '__main__':
    webCase()
