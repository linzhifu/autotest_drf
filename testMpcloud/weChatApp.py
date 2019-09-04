from appium import webdriver
import time

# 设置启动参数desired_caps
desired_caps = {
    "platformName": "Android",
    "deviceName": "R28M30YHMMX",
    "platformVersion": "9",
    "appPackage": "com.tencent.mm",
    "appActivity": ".ui.LauncherUI",
    # 设置app启动不重置
    "noReset": True,
    # 设置连接会话超时时间，单位s
    "newCommandTimeout": 60,
    # 使用Unicode编码方式发送字符
    "unicodeKeyboard": True,
    # 隐藏键盘
    "resetKeyboard": True
}

# 启动appium会话
driver = webdriver.Remote('http://127.0.0.1:4723/wd/hub', desired_caps)

# 设置隐形等待时间，单位s
driver.implicitly_wait(10)

# 等待微信首页打开
driver.wait_activity('.ui.LauncherUI', 10)
time.sleep(2)

# 获取屏幕尺寸
screem = driver.get_window_size()
print(screem)
# 下拉屏幕，打开微信小程序页面
driver.swipe(screem['width'] * 0.5, screem['width'] * 0.5,
             screem['height'] * 0.2, screem['height'] * 0.8, 1000)

# 点击量产云平台小程序
mpcloudBtn = driver.find_element_by_id('com.tencent.mm:id/jq')
mpcloudBtn.click()

# 等待量产云平台小程序打开
driver.wait_activity('.plugin.appbrand.ui.AppBrandUI', 10)
time.sleep(2)

# 点击数据统计
dataBtn = driver.find_element_by_xpath('//*[@text="数据统计"]')
dataBtn.click()
# 等待页面刷新
driver.wait_activity('.plugin.appbrand.ui.AppBrandUI', 10)
time.sleep(2)

# 点击返回
backBtn = driver.find_element_by_xpath('//*[@text="功能"]')
backBtn.click()
# 等待页面刷新
driver.wait_activity('.plugin.appbrand.ui.AppBrandUI', 10)
time.sleep(2)

# 点击消息管理
infoBtn = driver.find_element_by_xpath('//*[@text="消息管理"]')
infoBtn.click()
# 等待页面刷新
driver.wait_activity('.plugin.appbrand.ui.AppBrandUI', 10)
time.sleep(2)

# 关闭小程序
closeBtn = driver.find_element_by_accessibility_id('关闭')
closeBtn.click()
# 等待返回微信首页
driver.wait_activity('.ui.LauncherUI', 10)
time.sleep(2)

driver.quit()
