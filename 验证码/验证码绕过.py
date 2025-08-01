'''
# -*- coding: utf-8 -*-
"""
网络爬虫之用户名密码及验证码登陆：爬取知乎网站
"""

# 导入所需的模块
import requests  # 用于发送网络请求
import configparser  # 用于读取配置文件 config.ini


# 定义函数 create_session，用于创建一个带登录状态的会话对象
def create_session():
    # 创建 configparser 对象，用于读取配置文件
    cf = configparser.ConfigParser()

    # 读取当前目录下的 config.ini 文件
    cf.read('config.ini')

    # 读取配置文件中 [cookies] 部分的所有键值对
    cookies = cf.items('cookies')

    # 将 cookies 转换为字典格式，方便后续使用
    cookies = dict(cookies)

    # 打印 cookies（调试用）
    from pprint import pprint
    pprint(cookies)

    # 从配置文件中读取 email 字段
    email = cf.get('info', 'email')

    # 从配置文件中读取 password 字段
    password = cf.get('info', 'password')

    # 创建一个 requests 会话对象，用于保持登录状态
    session = requests.session()

    # 构造登录请求的数据（邮箱和密码）
    login_data = {'email': email, 'password': password}

    # 设置请求头信息，模拟浏览器访问
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Host': 'www.zhihu.com',
        'Referer': 'https://www.zhihu.com/',
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }


    # 向知乎邮箱登录接口发送 POST 请求
    r = session.post('https://www.zhihu.com/signin?next=%2F', data=login_data, headers=header)

    # 判断登录是否失败（r.json()['r'] == 1 表示失败）
    if r.json()['r'] == 1:
        print('Login Failed, reason is:')

        # 输出失败原因
        for m in r.json()['data']:
            print(r.json()['data'][m])

        print('So we use cookies to login in...')

        # 检查 cookies 是否有效
        has_cookies = False
        for key in cookies:
            if key != '__name__' and cookies[key] != '':
                has_cookies = True
                break

        # 如果 cookies 无效，抛出异常提示用户填写
        if has_cookies is False:
            raise ValueError('请填写config.ini文件中的cookies项.')
        else:
            # 使用 cookies 重新登录（模拟已登录状态）
            r = session.get('http://www.zhihu.com/login/email', cookies=cookies)  # 实现验证码登陆

    # 将登录后的响应内容写入 login.html 文件（调试用）
    with open('login.html', 'w') as fp:
        fp.write(r.content)

    # 返回 session 和 cookies，用于后续爬取需要登录的页面
    return session, cookies


# 主程序入口
if __name__ == '__main__':
    # 调用 create_session 函数，获取 session 和 cookies
    requests_session, requests_cookies = create_session()

    # 设置目标 URL（例如知乎的一个话题页面）
    url = 'http://www.zhihu.com/topic/19552832'

    # 使用 session 和 cookies 发送 GET 请求，访问需要登录的页面
    content = requests_session.get(url, cookies=requests_cookies).content  # 已登陆

    # 将爬取到的页面内容写入 url.html 文件（调试用）
    with open('url.html', 'w') as fp:
        fp.write(content)
'''

import requests
import configparser

# 定义函数：创建一个带有 Cookie 的 session
def create_session():
    # 创建配置文件解析器
    cf = configparser.ConfigParser()
    cf.read('config.ini')

    # 读取 cookies 部分，并转为字典
    cookies = dict(cf.items('cookies'))

    # 创建 requests 会话对象
    session = requests.Session()

    # 返回 session 和 cookies
    return session, cookies

# 主程序入口
if __name__ == '__main__':
    # 获取 session 和 cookies
    session, cookies = create_session()

    # 设置要爬取的目标 URL（知乎话题页）
    url = 'https://www.zhihu.com/'

    # 发送 GET 请求，带上 cookies
    response = session.get(url, cookies=cookies, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })

    # 输出状态码和部分响应内容，验证是否登录成功
    print("响应状态码:", response.status_code)
    print("前500字符内容:")
    print(response.text[:500])

    # 将爬取结果保存到文件（调试用）
    with open('zhihu_topic.html', 'w', encoding='utf-8') as f:
        f.write(response.text)

    print("页面内容已保存到 zhihu_topic.html")
