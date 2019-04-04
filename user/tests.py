# from django.test import TestCase, Client
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
from user.models import WebCase, CheckWebCase, TestRecord
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
import logging
from datetime import datetime
import os

# Create your tests here.

logging.basicConfig(
    level=logging.DEBUG, format='%(asctime)s-%(levelname)s-%(message)s')
logging.disable(logging.DEBUG)


# 记录测试log装饰器
def save_log(fuc):
    def wrapper(*args, **kwargs):
        testName = kwargs.get('testName')
        # 测试目录
        logData = datetime.now().strftime('%Y-%m-%d')
        LOGDIR = logData + '\\' + testName

        # 检查目录
        if os.path.exists(logData):
            pass
        else:
            os.mkdir(logData)

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


# class DemoTest(TestCase):
#     def test(self):
#         client = Client()
#         response = client.post('http://127.0.0.1:8000/v1/login/', {
#             "email": "linzhifu222@163.com",
#             "password": "123"
#         })
#         print(response.content)
#         self.assertEqual(True, True)


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
def webTest(url, host, webTypes, webManager, testName):
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


if __name__ == '__main__':
    webCase()
