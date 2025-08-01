"""
# coding:utf-8
import urllib.parse,urllib.request

url = "http://www.douban.com/"
data = {
    'name' : '18003279881',
    'password' : 'jNz.WRB8a8Y5FRs'
}
data = urllib.parse.urlencode(data).encode('utf-8')      # 编码工作，由 dict 转换成 str
req = urllib.request.Request(url = url, data = data)
response = urllib.request.urlopen(req)
print(response.read())
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# 自动下载并使用匹配的 ChromeDriver
service = Service(ChromeDriverManager().install())

# 创建浏览器
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
driver = webdriver.Chrome(service=service, options=options)

# 打开豆瓣登录页面
driver.get("https://accounts.douban.com/passport/login")

# 切换到账号密码登录
time.sleep(2)
driver.find_element(By.CLASS_NAME, "account-tab-account").click()

# 输入账号和密码
time.sleep(1)
driver.find_element(By.ID, "username").send_keys("18003279881")
driver.find_element(By.ID, "password").send_keys("jNz.WRB8a8Y5FRs")

input("请完成滑块验证并登录成功后，按回车继续...")

driver.get("https://www.douban.com/")
time.sleep(3)
print(driver.page_source)

driver.quit()
