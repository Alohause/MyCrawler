# coding:utf-8
import urllib.parse
import urllib.request

url = "http://www.baidu.com/s"
data = {
    'wd':'xx'                     # word 缩写，查询关键字参数，更通用的是 q (Google会用)
}
data = urllib.parse.urlencode(data)     # 编码工作，由 dict 转换成 str
full_url = url + "?" + data             # GET 请求发送
print(full_url)
response = urllib.request.urlopen(full_url)
print(response.read())
