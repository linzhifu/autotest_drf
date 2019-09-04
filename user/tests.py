# from django.test import TestCase, Client
from selenium import webdriver
from appium import webdriver as appdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
from user.models import WebCase, CheckWebCase, TestRecord, ApiCase, AppCase, CheckAppCase
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
import logging
from datetime import datetime, timedelta
import os
import requests
import time
import json
from testMpcloud import config, mpcloud
from django.core.cache import cache
# Create your tests here.

# 日子打印配置
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s-%(levelname)s-%(message)s')
logging.disable(logging.DEBUG)

# 前端自动化测试内容
pro_pm = {
    'role':
    '产品-产品工程师',
    'options': [{
        '个人资料': True,
    }, {
        '我的群组': True
    }, {
        '添加项目': True
    }, {
        '产品列表': True
    }, {
        '订单列表': True
    }]
}
mod_pm = {
    'role': '项目-产品工程师',
    'options': [{
        '个人资料': True
    }, {
        '我的群组': True
    }, {
        '产品列表': True
    }, {
        '订单列表': True
    }]
}
pro_rd = {
    'role':
    '产品-研发工程师',
    'options': [{
        '个人资料': True
    }, {
        '我的群组': True
    }, {
        '产品列表': True
    }, {
        '订单列表': True
    }, {
        '添加样品': True
    }]
}
mod_rd = {
    'role':
    '项目-研发工程师',
    'options': [{
        '个人资料': True
    }, {
        '我的群组': True
    }, {
        '产品列表': True
    }, {
        '订单列表': True
    }, {
        '添加样品': True
    }]
}
pro_te = {
    'role':
    '产品-测试工程师',
    'options': [{
        '个人资料': True
    }, {
        '我的群组': True
    }, {
        '产品列表': True
    }, {
        '订单列表': True
    }, {
        '添加样品': True
    }]
}
mod_te = {
    'role':
    '项目-测试工程师',
    'options': [{
        '个人资料': True
    }, {
        '我的群组': True
    }, {
        '产品列表': True
    }, {
        '订单列表': True
    }, {
        '添加样品': True
    }]
}
pro_ge = {
    'role':
    '产品-工艺工程师',
    'options': [{
        '个人资料': True
    }, {
        '我的群组': True
    }, {
        '产品列表': True
    }, {
        '订单列表': True
    }, {
        '添加样品': True
    }]
}
mod_ge = {
    'role':
    '项目-工艺工程师',
    'options': [{
        '个人资料': True
    }, {
        '我的群组': True
    }, {
        '产品列表': True
    }, {
        '订单列表': True
    }, {
        '添加样品': True
    }]
}
pro_pmc = {
    'role':
    '产品-pmc',
    'options': [{
        '个人资料': True
    }, {
        '我的群组': True
    }, {
        '产品列表': True
    }, {
        '创建订单': True
    }, {
        '订单列表': True
    }]
}
mod_pmc = {
    'role':
    '项目-pmc',
    'options': [{
        '个人资料': True
    }, {
        '我的群组': True
    }, {
        '产品列表': True
    }, {
        '创建订单': True
    }, {
        '订单列表': True
    }]
}
pro_pe = {
    'role': '产品-产线工程师',
    'options': [{
        '个人资料': True
    }, {
        '我的群组': True
    }, {
        '订单列表': True
    }]
}
mod_pe = {
    'role': '项目-产线工程师',
    'options': [{
        '个人资料': True
    }, {
        '我的群组': True
    }, {
        '订单列表': True
    }]
}
pro_pj = {
    'role': '产品-项目工程师',
    'options': [{
        '个人资料': True
    }, {
        '我的群组': True
    }, {
        '产品列表': True
    }, {
        '订单列表': True
    }]
}
mod_pj = {
    'role': '项目-项目工程师',
    'options': [{
        '个人资料': True
    }, {
        '我的群组': True
    }, {
        '产品列表': True
    }, {
        '订单列表': True
    }]
}
mpcloudCases = [
    pro_pm, mod_pm, pro_rd, mod_rd, pro_te, mod_te, pro_ge, mod_ge, pro_pmc,
    mod_pmc, pro_pe, mod_pe, pro_pj, mod_pj
]

# token配置
user_token = {
    'userid': '',
    'token': '',
}

# 用户登陆配置
loginCase = {
    'method': 'post',
    'url': '/api/v1/user/login',
    'params': {},
    'headers': {
        'content-type': 'application/json'
    },
    'json': {
        'email': '17388730192@163.com',
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
        logData = '../log/' + datetime.now().strftime('%Y-%m-%d')
        logType = logData + '/' + testType
        LOGDIR = logType + '/' + testName

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
        savePath = LOGDIR + '/' + '%s.log' % (logName)

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
            os.rename(savePath, LOGDIR + '/' + '%s-%s.log' % (logName, 'pass'))
        else:
            os.rename(savePath, LOGDIR + '/' + '%s-%s.log' % (logName, 'fail'))
        return resu

    return wrapper


# django项目测试示例（量产云平台）
# class DemoTest(TestCase):
#     def test(self):
#         client = Client()
#         url = 'http://127.0.0.1:8000/'
#         projectId = 52
#         response = client.get(url + '/api/v1/projectTest/',
#                               {"projectId": projectId})
#         print(response.content)
#         self.assertEqual(True, True)
def test():
    pass


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


# 获取测试记录
def get_record(object):
    today = timezone.now().date()
    test_records = []
    for i in range(6, -1, -1):
        records = {}
        test_time = today - timedelta(days=i)
        records['日期'] = test_time.strftime('%m/%d')
        content_type = ContentType.objects.get_for_model(object)
        test_record, _ = TestRecord.objects.get_or_create(
            content_type=content_type,
            object_id=object.pk,
            test_time=test_time)
        records['测试总数'] = test_record.test_all
        records['PASS'] = test_record.test_pass
        records['FAIL'] = test_record.test_fail
        test_records.append(records)
    return test_records


# 前端单元测试操作
def webCase(url, host, webType, webManager):
    try:
        desired_capabilities = {'platform': 'WINDOWS', 'browserName': 'chrome'}
        driver = webdriver.Remote(host,
                                  desired_capabilities=desired_capabilities)
    except Exception:
        # opt = webdriver.ChromeOptions()
        # opt.set_headless()
        # # 谷歌文档提到需要加上这个属性来规避bug
        # opt.add_argument('--disable-gpu')
        # # 指定浏览器分辨率
        # opt.add_argument('window-size=1920x3000')
        # driver = webdriver.Chrome(options=opt)
        # driver = webdriver.Chrome()
        data = {'errcode': 1, 'errmsg': '未识别到浏览器服务端，请检查是否打开'}
        return data
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
            element = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, webCase.webcss)),
                                 message='找不到元素-%s' % (webCase.webcss))
            if webCase.weboprate:
                method = getattr(element, webCase.weboprate)
                if webCase.webparam:
                    method(webCase.webparam)
                else:
                    method()
            sleep(1)
        except Exception as e:
            print(webCase.webname + ' ：', e)
            webType.result = False
            webType.save()
            add_one_test_record(webType, False)
            webManager.result = False
            webManager.save()
            webManager.project.webresult = False
            webManager.project.save()
            data['errcode'] = 101
            data['errmsg'] = webCase.webname + ' ：操作异常'
            data['detail'] = str(e)
            driver.quit()
            logging.info(webType.typename + '-FAIL')
            return data

    # 验证文本
    checkWebCases = CheckWebCase.objects.filter(testType=webType.id)
    for checkWebCase in checkWebCases:
        try:
            element = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, checkWebCase.webcss)),
                                 message='找不到元素-%s' % (checkWebCase.webcss))
            if checkWebCase.weboprate:
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
            print(checkWebCase.webname + ' ：', e)
            webType.result = False
            webType.save()
            add_one_test_record(webType, False)
            webManager.result = False
            webManager.save()
            webManager.project.webresult = False
            webManager.project.save()
            data['errcode'] = 103
            data['errmsg'] = checkWebCase.webname + ' ：操作异常'
            data['detail'] = str(e)
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
        driver = webdriver.Remote(host,
                                  desired_capabilities=desired_capabilities)
    except Exception:
        # opt = webdriver.ChromeOptions()
        # opt.set_headless()
        # # 谷歌文档提到需要加上这个属性来规避bug
        # opt.add_argument('--disable-gpu')
        # # 指定浏览器分辨率
        # opt.add_argument('window-size=1920x3000')
        # driver = webdriver.Chrome(options=opt)
        # driver = webdriver.Chrome()
        data = {'errcode': 1, 'errmsg': '未识别到浏览器服务端，请检查是否打开'}
        return data
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
                    element = wait.until(EC.presence_of_element_located(
                        (By.CSS_SELECTOR, webCase.webcss)),
                                         message='找不到元素-%s' % (webCase.webcss))
                    if webCase.weboprate:
                        method = getattr(element, webCase.weboprate)
                        if webCase.webparam:
                            method(webCase.webparam)
                        else:
                            method()
                    sleep(1)
                except Exception as e:
                    print(webCase.webname + ' ：', e)
                    webType.result = False
                    webType.save()
                    webManager.result = False
                    webManager.save()
                    webManager.project.webresult = False
                    webManager.project.save()
                    add_one_test_record(webType, False)
                    add_one_test_record(webManager, False)
                    data['errcode'] = 101
                    data[
                        'errmsg'] = webType.typename + '-' + webCase.webname + ' ：操作异常'
                    data['detail'] = str(e)
                    driver.quit()
                    logging.info(webType.typename + '-FAIL')
                    return data

            # 验证文本
            checkWebCases = CheckWebCase.objects.filter(testType=webType.id)
            for checkWebCase in checkWebCases:
                try:
                    element = wait.until(EC.presence_of_element_located(
                        (By.CSS_SELECTOR, checkWebCase.webcss)),
                                         message='找不到元素-%s' %
                                         (checkWebCase.webcss))
                    if checkWebCase.weboprate:
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
                            webManager.project.webresult = False
                            webManager.project.save()
                            add_one_test_record(webType, False)
                            add_one_test_record(webManager, False)
                            data['errcode'] = 102
                            data['errmsg'] = webType.typename + '-' + checkWebCase.webname \
                                + '：' + checkWebCase.checktext + ' != ' + text
                            driver.quit()
                            logging.info(webType.typename + '-FAIL')
                            return data

                except Exception as e:
                    print(checkWebCase.webname + '：', e)
                    webType.result = False
                    webType.save()
                    webManager.result = False
                    webManager.save()
                    webManager.project.webresult = False
                    webManager.project.save()
                    add_one_test_record(webType, False)
                    add_one_test_record(webManager, False)
                    data['errcode'] = 103
                    data[
                        'errmsg'] = webType.typename + '-' + checkWebCase.webname + ' ：操作异常'
                    data['detail'] = str(e)
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


# 移动端单元测试操作
def appCase(host, appType, appManager):
    # 测试结果
    data = {'errcode': 0, 'errmsg': 'ok'}
    text = ''
    driver = ''
    el = ''
    # 启动appium会话
    try:
        desired_caps = parse_obj(json.loads(appManager.desired_caps))
        # print(desired_caps)
        driver = appdriver.Remote(host, desired_caps)
        # 设置隐形等待时间，单位s
        driver.implicitly_wait(10)
    except Exception:
        data = {'errcode': 1, 'errmsg': '未识别到浏览器服务端，请检查是否打开'}
        return data
    # 等待程序页面启动成功
    driver.wait_activity(desired_caps['appActivity'], 10)
    sleep(1)
    # 操作前端页面
    appCases = AppCase.objects.filter(testType=appType.id)
    for appCase in appCases:
        try:
            # 选择元素并操作
            if appCase.selectmethod:
                # print('选择元素并操作')
                method = getattr(driver, appCase.selectmethod)
                if appCase.selectparam:
                    el = method(appCase.selectparam)
                else:
                    raise Exception('元素定位参数为空')
                # 元素操作
                if appCase.appoprate:
                    method = getattr(el, appCase.appoprate)
                    if appCase.appparam:
                        method(appCase.appparam)
                    else:
                        method()
                sleep(1)
            # 操作界面
            elif appCase.appoprate:
                # print('操作界面')
                method = getattr(driver, appCase.appoprate)
                # print(method)
                if appCase.appparam:
                    # print(appCase.appparam.split(','))
                    method(*(appCase.appparam.split(',')))
                else:
                    method()
                sleep(1)
            else:
                raise Exception('元素定位方法和元素操作方法都为空')
        except Exception as e:
            print(appCase.appname + ' ：', e)
            appType.result = False
            appType.save()
            add_one_test_record(appType, False)
            appManager.result = False
            appManager.save()
            appManager.project.appresult = False
            appManager.project.save()
            data['errcode'] = 101
            data['errmsg'] = appCase.appname + ' ：操作异常'
            data['detail'] = str(e)
            driver.quit()
            logging.info(appType.typename + '-FAIL')
            return data

    # 验证文本
    text = ''
    checkAppCases = CheckAppCase.objects.filter(testType=appType.id)
    for checkAppCase in checkAppCases:
        try:
            # 选择元素
            if checkAppCase.selectmethod:
                method = getattr(driver, checkAppCase.selectmethod)
                if checkAppCase.selectparam:
                    el = method(checkAppCase.selectparam)
                else:
                    raise Exception('元素定位参数为空')
            else:
                raise Exception('元素定位方法为空')
            sleep(1)
            # 元素操作
            if checkAppCase.appoprate:
                method = getattr(el, checkAppCase.appoprate)
                if checkAppCase.appparam:
                    text = method(checkAppCase.appparam)
                else:
                    text = method()
                sleep(1)
                if text != checkAppCase.checktext:
                    appType.result = False
                    appType.save()
                    add_one_test_record(appType, False)
                    appManager.result = False
                    appManager.save()
                    data['errcode'] = 102
                    data['errmsg'] = checkAppCase.appname \
                        + '：' + checkAppCase.checktext + ' != ' + text
                    driver.quit()
                    logging.info(appType.typename + '-FAIL')
                    return data

        except Exception as e:
            print(checkAppCase.appname + ' ：', e)
            appType.result = False
            appType.save()
            add_one_test_record(appType, False)
            appManager.result = False
            appManager.save()
            appManager.project.webresult = False
            appManager.project.save()
            data['errcode'] = 103
            data['errmsg'] = checkAppCase.appname + ' ：操作异常'
            data['detail'] = str(e)
            driver.quit()
            logging.info(appType.typename + '-FAIL')
            return data

    appType.result = True
    appType.save()
    add_one_test_record(appType, True)
    logging.info(appType.typename + '-PASS')

    driver.quit()
    return data


# 移动端整体测试
@save_log
def appTest(host, appTypes, appManager, testName, type):
    # 测试结果
    data = {'errcode': 0, 'errmsg': 'ok'}
    text = ''
    driver = ''
    el = ''
    # 启动appium会话
    try:
        desired_caps = parse_obj(json.loads(appManager.desired_caps))
        # print(desired_caps)
        driver = appdriver.Remote(host, desired_caps)
        # 设置隐形等待时间，单位s
        driver.implicitly_wait(10)
    except Exception:
        data = {'errcode': 1, 'errmsg': '未识别到浏览器服务端，请检查是否打开'}
        return data
    # 等待程序页面启动成功
    driver.wait_activity(desired_caps['appActivity'], 10)
    sleep(1)

    for appType in appTypes:
        if appType.is_test:
            # 操作前端页面
            appCases = AppCase.objects.filter(testType=appType.id)
            for appCase in appCases:
                try:
                    # 选择元素并操作
                    if appCase.selectmethod:
                        # print('选择元素并操作')
                        method = getattr(driver, appCase.selectmethod)
                        if appCase.selectparam:
                            el = method(appCase.selectparam)
                        else:
                            raise Exception('元素定位参数为空')
                        # 元素操作
                        if appCase.appoprate:
                            method = getattr(el, appCase.appoprate)
                            if appCase.appparam:
                                method(appCase.appparam)
                            else:
                                method()
                        sleep(1)
                    # 操作界面
                    elif appCase.appoprate:
                        # print('操作界面')
                        method = getattr(driver, appCase.appoprate)
                        # print(method)
                        if appCase.appparam:
                            # print(appCase.appparam.split(','))
                            method(*(appCase.appparam.split(',')))
                        else:
                            method()
                        sleep(1)
                    else:
                        raise Exception('元素定位方法和元素操作方法都为空')
                except Exception as e:
                    print(appCase.appname + ' ：', e)
                    appType.result = False
                    appType.save()
                    add_one_test_record(appType, False)
                    appManager.result = False
                    appManager.save()
                    appManager.project.appresult = False
                    appManager.project.save()
                    data['errcode'] = 101
                    data['errmsg'] = appCase.appname + ' ：操作异常'
                    data['detail'] = str(e)
                    driver.quit()
                    logging.info(appType.typename + '-FAIL')
                    return data

            # 验证文本
            text = ''
            checkAppCases = CheckAppCase.objects.filter(testType=appType.id)
            for checkAppCase in checkAppCases:
                try:
                    # 选择元素
                    if checkAppCase.selectmethod:
                        method = getattr(driver, checkAppCase.selectmethod)
                        if checkAppCase.selectparam:
                            el = method(checkAppCase.selectparam)
                        else:
                            raise Exception('元素定位参数为空')
                    else:
                        raise Exception('元素定位方法为空')
                    sleep(1)
                    # 元素操作
                    if checkAppCase.appoprate:
                        method = getattr(el, checkAppCase.appoprate)
                        if checkAppCase.appparam:
                            text = method(checkAppCase.appparam)
                        else:
                            text = method()
                        sleep(1)
                        if text != checkAppCase.checktext:
                            appType.result = False
                            appType.save()
                            add_one_test_record(appType, False)
                            appManager.result = False
                            appManager.save()
                            data['errcode'] = 102
                            data['errmsg'] = checkAppCase.appname \
                                + '：' + checkAppCase.checktext + ' != ' + text
                            driver.quit()
                            logging.info(appType.typename + '-FAIL')
                            return data

                except Exception as e:
                    print(checkAppCase.appname + ' ：', e)
                    appType.result = False
                    appType.save()
                    add_one_test_record(appType, False)
                    appManager.result = False
                    appManager.save()
                    appManager.project.webresult = False
                    appManager.project.save()
                    data['errcode'] = 103
                    data['errmsg'] = checkAppCase.appname + ' ：操作异常'
                    data['detail'] = str(e)
                    driver.quit()
                    logging.info(appType.typename + '-FAIL')
                    return data

        appType.result = True
        appType.save()
        add_one_test_record(appType, True)
        logging.info(appType.typename + '-PASS')

    appManager.result = True
    appManager.save()
    add_one_test_record(appManager, True)
    driver.quit()
    return data


# 赋值变量
def asign_var(data):
    # 赋值系统变量
    if data.startswith('$'):
        if data == '$Date':
            return int(time.time())
        elif data == '$true':
            return True
        elif data == '$false':
            return False
        else:
            return data
    # 赋值系统变量
    # 整数型
    elif data.startswith('&i-'):
        return int(cache.get(data[3:]))
    # 字符串
    elif data.startswith('&'):
        return cache.get(data[1:])
    # 列表
    elif data.startswith('[') and data.endswith(']'):
        _data = json.loads(data)
        for i in range(len(_data)):
            if isinstance(_data[i], str) or isinstance(_data[i], list):
                _data[i] = asign_var(_data[i])
        return json.dumps(_data)
    else:
        return data


# 遍历对象，赋值变量
def parse_obj(data):
    if isinstance(data, str):
        return asign_var(data)
    elif isinstance(data, dict):
        for key in data:
            data[key] = parse_obj(data[key])
        return data
    elif isinstance(data, list):
        for i in range(len(data)):
            data[i] = parse_obj(data[i])
        return data
    else:
        return data


# 遍历对象，保存自定义变量
def save_userObj(data, data1, key='response'):
    if isinstance(data, str):
        if data.startswith('&'):
            cache.set(data[1:], data1)
        else:
            if data == data1:
                pass
            else:
                raise Exception(key + ' 不一致')
    elif isinstance(data, dict):
        if isinstance(data1, dict):
            if data == {} and data != data1:
                raise Exception(key + ' 不一致')
            for _data in data:
                if data.get(_data) is not None:
                    save_userObj(data[_data], data1[_data], _data)
                else:
                    raise Exception(_data + ' 不一致')
        else:
            raise Exception(key + ' 不一致')
    elif isinstance(data, list):
        if isinstance(data1, list):
            if data == [] and data != data1:
                raise Exception(key + ' 不一致')
            for _data in range(len(data)):
                if _data < len(data1):
                    save_userObj(data[_data], data1[_data], _data)
                else:
                    raise Exception(_data + ' 不一致')
        else:
            raise Exception(key + ' 不一致')
    else:
        if data == data1:
            pass
        else:
            raise Exception(key + ' 不一致')


# API请求
def doTest(case, RESTAPI_DOMAIN):
    start = time.time()
    response = ''
    error = None
    # print(case)
    try:
        response = requests.request(method=case['method'],
                                    url=RESTAPI_DOMAIN + case['url'],
                                    params=case['params'],
                                    json=case['json'],
                                    data=case['form'],
                                    headers=case['headers'],
                                    verify=False)
    except requests.exceptions.ConnectionError:
        error = "ConnectionError"
    # except requests.exceptions.HTTPError:
    #     error = "HTTPError"
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
        except Exception:
            error = '返回数据不是JSON对象'
    # print(rev)
    if error is None:
        if not case['response']:
            error = 'response为空'
    if error is None:
        try:
            save_userObj(case['response'], rev)
        except Exception as e:
            error = str(e)
    result = {'time': str(round(timeval, 2)), 'error': error, 'response': rev}
    return result


# 设置管理员
def setAdmin(apiCase, RESTAPI_DOMAIN, testUserInfo):
    # print('设置管理员----------------------------------------')
    adminCase = {}
    adminCase['method'] = 'post'
    adminCase['url'] = '/api/v1/role/user'
    adminCase['params'] = {
        'userid': testUserInfo.get('adminUserId'),
        'token': testUserInfo.get('adminUserToken')
    }
    adminCase['json'] = {
        'roleid': 1,
        'userid': int(testUserInfo.get('testUserId'))
    }
    adminCase['form'] = ''
    adminCase['response'] = {"errcode": 0, "errmsg": "ok"}
    adminCase['headers'] = {'content-type': 'application/json'}
    result = doTest(adminCase, RESTAPI_DOMAIN)
    return result


# 取消设置管理员
def deleteAdmin(apiCase, RESTAPI_DOMAIN, testUserInfo):
    # print('取消管理员----------------------------------------')
    adminCase = {}
    adminCase['method'] = 'delete'
    adminCase['url'] = '/api/v1/role/user'
    adminCase['params'] = {
        'userid': testUserInfo.get('adminUserId'),
        'token': testUserInfo.get('adminUserToken')
    }
    adminCase['json'] = {
        'roleid': 1,
        'userid': int(testUserInfo.get('testUserId'))
    }
    adminCase['form'] = ''
    adminCase['response'] = {"errcode": 0, "errmsg": "ok"}
    adminCase['headers'] = {'content-type': 'application/json'}
    result = doTest(adminCase, RESTAPI_DOMAIN)
    return result


# 授权
def setAuth(apiCase, RESTAPI_DOMAIN, testUserInfo):
    # print('设置权限----------------------------------------')
    authCase = {}
    authCase['method'] = 'post'
    authCase['url'] = '/api/v1/role/permission'
    authCase['params'] = {
        'userid': testUserInfo.get('adminUserId'),
        'token': testUserInfo.get('adminUserToken')
    }
    authCase['json'] = {
        "operator": {
            "type": apiCase.operatorType,
            "id": int(apiCase.objectId)
        },
        "object": {
            "type": apiCase.objectType,
            "id": int(apiCase.objectId)
        },
        "actions": apiCase.actions.split(',')
    }
    authCase['form'] = ''
    authCase['response'] = {"errcode": 0, "errmsg": "ok"}
    authCase['headers'] = {'content-type': 'application/json'}
    # print(authCase)
    result = doTest(authCase, RESTAPI_DOMAIN)
    return result


# 取消授权
def deleteAuth(apiCase, RESTAPI_DOMAIN, testUserInfo):
    # print('取消权限----------------------------------------')
    authCase = {}
    authCase['method'] = 'delete'
    authCase['url'] = '/api/v1/role/permission'
    authCase['params'] = {
        'userid': testUserInfo.get('adminUserId'),
        'token': testUserInfo.get('adminUserToken')
    }
    authCase['json'] = {
        "operator": {
            "type": apiCase.operatorType,
            "id": int(apiCase.objectId)
        },
        "object": {
            "type": apiCase.objectType,
            "id": int(apiCase.objectId)
        },
        "actions": apiCase.actions.split(',')
    }
    authCase['form'] = ''
    authCase['response'] = {"errcode": 0, "errmsg": "ok"}
    authCase['headers'] = {'content-type': 'application/json'}
    # print(authCase)
    result = doTest(authCase, RESTAPI_DOMAIN)
    return result


# 后端API单元测试
def apiCase(url, apiType, apiManager, testUserInfo):
    data = {'errcode': 0, 'errmsg': 'ok'}
    RESTAPI_DOMAIN = url
    # 先登陆获取测试用户token
    # doTest(loginCase, RESTAPI_DOMAIN)
    apiCases = ApiCase.objects.filter(testType=apiType.id)
    for apiCase in apiCases:
        # 是否需要设置为管理员
        if apiCase.isAdmin:
            result = setAdmin(apiCase, RESTAPI_DOMAIN, testUserInfo)
            if result['error']:
                data['errcode'] = 101
                data['errmsg'] = apiCase.apiname + '-设置管理员' + '：' + result[
                    'error']
                apiCase.result = False
                apiCase.save()
                apiType.result = False
                apiType.save()
                apiManager.project.webresult = False
                apiManager.project.save()
                add_one_test_record(apiType, False)
                apiManager.result = False
                apiManager.save()
                logging.info(apiCase.apiname + '-' + apiCase.apiurl + '-' +
                             result['time'] + '-' + 'FAIL')
                return data
        # 是否需要添加权限
        if apiCase.isAuth:
            result = setAuth(apiCase, RESTAPI_DOMAIN, testUserInfo)
            if result['error']:
                data['errcode'] = 101
                data['errmsg'] = apiCase.apiname + '-设置权限' + '：' + result[
                    'error']
                apiCase.result = False
                apiCase.save()
                apiType.result = False
                apiType.save()
                apiManager.project.webresult = False
                apiManager.project.save()
                add_one_test_record(apiType, False)
                apiManager.result = False
                apiManager.save()
                logging.info(apiCase.apiname + '-' + apiCase.apiurl + '-' +
                             result['time'] + '-' + 'FAIL')
                return data
        # 格式化参数
        case = {}
        # params
        try:
            params = json.loads(apiCase.apiparam)
            for key in params:
                params[key] = asign_var(params[key])
        except Exception:
            params = ''
        # print(params)

        # body_json
        if apiCase.contentType == 'application/json':
            case['headers'] = {'content-type': 'application/json'}
            try:
                body_json = json.loads(apiCase.apijson)
                body_json = parse_obj(body_json)
            except Exception:
                body_json = ''
            body_form = ''

        # body_form
        if apiCase.contentType == 'application/x-www-form-urlencoded':
            case['headers'] = {'content-type': 'multipart/form-data'}
            try:
                body_form = json.loads(apiCase.apijson)
                for _key in body_form:
                    body_form[_key] = body_form[_key][5:]
                body_form = parse_obj(body_form)
            except Exception:
                body_form = ''
            body_json = ''

        # response
        try:
            response = json.loads(apiCase.apiresponse)
        except Exception:
            response = ''

        case['method'] = apiCase.apimethod
        case['url'] = apiCase.apiurl
        case['params'] = params
        case['json'] = body_json
        case['form'] = body_form
        case['response'] = response
        # case['headers'] = {'content-type': apiCase.contentType}

        # print(case)
        # 发送请求
        result = doTest(case, RESTAPI_DOMAIN)
        if result['error']:
            data['errcode'] = 101
            data['errmsg'] = apiCase.apiname + '：' + result['error']
            data['detail'] = result['response']
            apiCase.result = False
            apiCase.save()
            apiType.result = False
            apiType.save()
            apiManager.project.webresult = False
            apiManager.project.save()
            add_one_test_record(apiType, False)
            apiManager.result = False
            apiManager.save()
            logging.info(apiCase.apiname + '-' + apiCase.apiurl + '-' +
                         result['time'] + '-' + 'FAIL')
            return data

        # 是否需要取消设置为管理员
        if apiCase.isAdmin:
            result = deleteAdmin(apiCase, RESTAPI_DOMAIN, testUserInfo)
            if result['error']:
                data['errcode'] = 101
                data['errmsg'] = apiCase.apiname + '-取消管理员' + '：' + result[
                    'error']
                apiCase.result = False
                apiCase.save()
                apiType.result = False
                apiType.save()
                apiManager.project.webresult = False
                apiManager.project.save()
                add_one_test_record(apiType, False)
                apiManager.result = False
                apiManager.save()
                logging.info(apiCase.apiname + '-' + apiCase.apiurl + '-' +
                             result['time'] + '-' + 'FAIL')
                return data
        # 是否需要删除权限
        if apiCase.isAuth:
            result = deleteAuth(apiCase, RESTAPI_DOMAIN, testUserInfo)
            if result['error']:
                data['errcode'] = 101
                data['errmsg'] = apiCase.apiname + '-删除权限' + '：' + result[
                    'error']
                apiCase.result = False
                apiCase.save()
                apiType.result = False
                apiType.save()
                apiManager.project.webresult = False
                apiManager.project.save()
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
# 后端模块测试
def apiTest(url, apiTypes, apiManager, testName, type, testUserInfo):
    data = {'errcode': 0, 'errmsg': 'ok'}
    RESTAPI_DOMAIN = url

    # 先登陆获取token
    # doTest(loginCase, RESTAPI_DOMAIN)

    for apiType in apiTypes:
        if apiType.is_test:
            apiCases = ApiCase.objects.filter(testType=apiType.id)
            for apiCase in apiCases:
                # 是否需要设置为管理员
                if apiCase.isAdmin:
                    result = setAdmin(apiCase, RESTAPI_DOMAIN, testUserInfo)
                    if result['error']:
                        data['errcode'] = 101
                        data[
                            'errmsg'] = apiCase.apiname + '-设置管理员' + '：' + result[
                                'error']
                        apiCase.result = False
                        apiCase.save()
                        apiType.result = False
                        apiType.save()
                        apiManager.project.webresult = False
                        apiManager.project.save()
                        add_one_test_record(apiType, False)
                        apiManager.result = False
                        apiManager.save()
                        logging.info(apiCase.apiname + '-' + apiCase.apiurl +
                                     '-' + result['time'] + '-' + 'FAIL')
                        return data
                # 是否需要添加权限
                if apiCase.isAuth:
                    result = setAuth(apiCase, RESTAPI_DOMAIN, testUserInfo)
                    if result['error']:
                        data['errcode'] = 101
                        data[
                            'errmsg'] = apiCase.apiname + '-设置权限' + '：' + result[
                                'error']
                        apiCase.result = False
                        apiCase.save()
                        apiType.result = False
                        apiType.save()
                        apiManager.project.webresult = False
                        apiManager.project.save()
                        add_one_test_record(apiType, False)
                        apiManager.result = False
                        apiManager.save()
                        logging.info(apiCase.apiname + '-' + apiCase.apiurl +
                                     '-' + result['time'] + '-' + 'FAIL')
                        return data

                # 格式化参数
                case = {}
                # params
                try:
                    params = json.loads(apiCase.apiparam)
                    for key in params:
                        params[key] = asign_var(params[key])
                except Exception:
                    params = ''
                # print(params)

                # body_json
                if apiCase.contentType == 'application/json':
                    try:
                        body_json = json.loads(apiCase.apijson)
                        body_json = parse_obj(body_json)
                    except Exception:
                        body_json = ''
                    body_form = ''

                # body_form
                if apiCase.contentType == 'application/x-www-form-urlencoded':
                    try:
                        body_form = json.loads(apiCase.apijson)
                        for _key in body_form:
                            body_form[_key] = body_form[_key][5:]
                        body_form = parse_obj(body_form)
                    except Exception:
                        body_form = ''
                    body_json = ''

                # response
                try:
                    response = json.loads(apiCase.apiresponse)
                except Exception:
                    response = ''

                case['method'] = apiCase.apimethod
                case['url'] = apiCase.apiurl
                case['params'] = params
                case['json'] = body_json
                case['form'] = body_form
                case['response'] = response
                case['headers'] = {'content-type': apiCase.contentType}

                # print(case)
                # 发送请求
                result = doTest(case, RESTAPI_DOMAIN)
                if result['error']:
                    data['errcode'] = 101
                    data[
                        'errmsg'] = apiType.typename + '-' + apiCase.apiname + '：' + result[
                            'error']
                    data['detail'] = result['response']
                    apiCase.result = False
                    apiCase.save()
                    apiType.result = False
                    apiType.save()
                    apiManager.result = False
                    apiManager.save()
                    apiManager.project.webresult = False
                    apiManager.project.save()
                    add_one_test_record(apiType, False)
                    add_one_test_record(apiManager, False)
                    logging.info(apiCase.apiname + '-' + apiCase.apiurl + '-' +
                                 result['time'] + '-' + 'FAIL')
                    return data

                # 是否需要取消设置为管理员
                if apiCase.isAdmin:
                    result = deleteAdmin(apiCase, RESTAPI_DOMAIN, testUserInfo)
                    if result['error']:
                        data['errcode'] = 101
                        data[
                            'errmsg'] = apiCase.apiname + '-取消管理员' + '：' + result[
                                'error']
                        apiCase.result = False
                        apiCase.save()
                        apiType.result = False
                        apiType.save()
                        apiManager.project.webresult = False
                        apiManager.project.save()
                        add_one_test_record(apiType, False)
                        apiManager.result = False
                        apiManager.save()
                        logging.info(apiCase.apiname + '-' + apiCase.apiurl +
                                     '-' + result['time'] + '-' + 'FAIL')
                        return data
                # 是否需要删除权限
                if apiCase.isAuth:
                    result = deleteAuth(apiCase, RESTAPI_DOMAIN, testUserInfo)
                    if result['error']:
                        data['errcode'] = 101
                        data[
                            'errmsg'] = apiCase.apiname + '-删除权限' + '：' + result[
                                'error']
                        apiCase.result = False
                        apiCase.save()
                        apiType.result = False
                        apiType.save()
                        apiManager.project.webresult = False
                        apiManager.project.save()
                        add_one_test_record(apiType, False)
                        apiManager.result = False
                        apiManager.save()
                        logging.info(apiCase.apiname + '-' + apiCase.apiurl +
                                     '-' + result['time'] + '-' + 'FAIL')
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


# 量产云平台前端自动化单元测试
def testMpcloudCase(host, case):
    result = {}
    user = {}

    # 判断是哪个角色测试，进行角色配置
    if case.get('role') == '产品-产品工程师':
        user = config.USER_PRO_PM
    elif case.get('role') == '项目-产品工程师':
        user = config.USER_MOD_PM
    elif case.get('role') == '产品-研发工程师':
        user = config.USER_PRO_RD
    elif case.get('role') == '项目-研发工程师':
        user = config.USER_MOD_RD
    elif case.get('role') == '产品-测试工程师':
        user = config.USER_PRO_TE
    elif case.get('role') == '项目-测试工程师':
        user = config.USER_MOD_TE
    elif case.get('role') == '产品-工艺工程师':
        user = config.USER_PRO_GE
    elif case.get('role') == '项目-工艺工程师':
        user = config.USER_MOD_GE
    elif case.get('role') == '产品-pmc':
        user = config.USER_PRO_PMC
    elif case.get('role') == '项目-pmc':
        user = config.USER_MOD_PMC
    elif case.get('role') == '产品-产线工程师':
        user = config.USER_PRO_PE
    elif case.get('role') == '项目-产线工程师':
        user = config.USER_MOD_PE
    elif case.get('role') == '产品-项目工程师':
        user = config.USER_PRO_PJ
    elif case.get('role') == '项目-项目工程师':
        user = config.USER_MOD_PJ

    # 根据用户选项判断测试项是否需要测试
    for option in case.get('options'):
        if '个人资料' in option:
            user['updateUserInfoEnable'] = option['个人资料']
        if '我的群组' in option:
            user['teamEnable'] = option['我的群组']
        if '添加项目' in option:
            user['addModEnable'] = option['添加项目']
        if '产品列表' in option:
            user['proLisEnable'] = option['产品列表']
        if '创建订单' in option:
            user['createOrderEnable'] = option['创建订单']
        if '订单列表' in option:
            user['orderListEnable'] = option['订单列表']
        if '添加样品' in option:
            user['createSampleEnable'] = option['添加样品']

    # 尝试远程启动客户端浏览器，启动失败再在服务器端启动浏览器
    try:
        desired_capabilities = {'platform': 'WINDOWS', 'browserName': 'chrome'}
        driver = webdriver.Remote(host,
                                  desired_capabilities=desired_capabilities)
    except Exception as E:
        # opt = webdriver.ChromeOptions()
        # opt.set_headless()
        # # 谷歌文档提到需要加上这个属性来规避bug
        # opt.add_argument('--disable-gpu')
        # # 指定浏览器分辨率
        # opt.add_argument('window-size=1920x3000')
        # driver = webdriver.Chrome(options=opt)
        # driver = webdriver.Chrome()
        result['errcode'] = 1
        result['errmsg'] = '未识别到浏览器服务端，请检查是否打开'
        result['detail'] = str(E)
        return result

    result = mpcloud.main(driver, user)
    return result


if __name__ == '__main__':
    test()
