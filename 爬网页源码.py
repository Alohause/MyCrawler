import requests

url = "http://news.163.com/rank"
res = requests.get(url)
content = res.content
print(content.decode("utf-8"))