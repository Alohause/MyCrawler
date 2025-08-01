"""
# coding:utf-8
import urllib.parse,urllib.request

url = "http://testphp.vulnweb.com/login.php"
data = {
    'uname' : 'test',
    'pass' : 'test',
    'submit' : 'login'
}
data = urllib.parse.urlencode(data).encode('utf-8')
req = urllib.request.Request(url = url, data = data)
response = urllib.request.urlopen(req)
print(response.read())
"""

import requests

# 会话对象
session = requests.Session()
login_url = "http://testphp.vulnweb.com/login.php"
data = {
    "uname": "test",
    "pass": "test",
    "submit": "login"
}

session.post(login_url, data=data)
res = session.get("http://testphp.vulnweb.com/userinfo.php")
print(res.text)
