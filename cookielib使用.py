"""
import requests

# 创建 Session 对象（自动管理 Cookie）
session = requests.Session()

# 登录地址和用户页地址
login_url = 'http://127.0.0.1:5000/'
userinfo_url = 'http://127.0.0.1:5000/userinfo'

# 登录表单数据
data = {
    'username': 'testuser',
    'password': '123456'
}

# 1. 模拟 POST 登录
res1 = session.post(login_url, data=data)
print("登录状态码：", res1.status_code)

# 2. 访问登录后的页面
res2 = session.get(userinfo_url)
print("用户信息页面状态码：", res2.status_code)
print("\n页面内容预览：\n", res2.text[:500])
"""

# coding:utf-8
import urllib.request
import urllib.parse
import http.cookiejar

# 1. 创建 CookieJar 实例（可换成 MozillaCookieJar 保存到文件）
cookie_jar = http.cookiejar.CookieJar()

# 2. 构建带 Cookie 处理器的 opener
handler = urllib.request.HTTPCookieProcessor(cookie_jar)
opener = urllib.request.build_opener(handler)

# 3. 登录地址（你 Flask 本地网站）
login_url = "http://127.0.0.1:5000/"

# 4. 构造登录表单数据
data = {
    "username": "testuser",
    "password": "123456"
}
encoded_data = urllib.parse.urlencode(data).encode("utf-8")

# 5. 构造请求对象
headers = {
    "User-Agent": "Mozilla/5.0"
}
request = urllib.request.Request(login_url, data=encoded_data, headers=headers)

# 6. 发起登录请求（此时服务器会设置 session cookie）
response = opener.open(request)
print("登录响应状态码:", response.getcode())

# 7. 访问登录后的用户信息页
userinfo_url = "http://127.0.0.1:5000/userinfo"
res = opener.open(userinfo_url)
html = res.read().decode("utf-8")

# 8. 检查是否登录成功
if "欢迎" in html or "用户信息" in html:
    print("\n登录成功，抓取到用户信息页！")
else:
    print("\n登录失败，未登录状态。")

# 9. 显示部分内容
print("\n页面内容预览\n")
print(html[:500])
